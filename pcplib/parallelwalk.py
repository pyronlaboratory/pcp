# Copyright Genome Research Ltd 2014
# Author gmpc@sanger.ac.uk
# This program is released under the GNU Public License V2 or later (GPLV2+)
from mpi4py import MPI
import os
import random
import stat
import readdir
import time
import safestat
from collections import deque
class ParallelWalk():
    """
    Manages communication and data processing between processes in a parallel
    environment. It has methods for sending and receiving data, checking for
    termination, and gathering results.

    Attributes:
        comm (MPIComm): Used to represent the MPI communicator object that manages
            communication between
            processes in a parallel walker.
        rank (int): 0-based indexing of the walker's rank in the MPI communication.
        workers (int): Used to store the total number of processes in the MPI communication.
        others (list): Used to store a range of process IDs excluding the current
            rank's ID, which is used for communication purposes.
        nextworker (int): 1-based index of the next worker to receive a token after
            the current worker. It is used to track the progress of work distribution
            among workers in a parallel walk algorithm.
        colour (str): Used to track the color of each walker in a parallel processing
            environment, with values of "White" or "Black". It is used to determine
            when a walker should send a shutdown message to its peers.
        token (str): Used to keep track of the work token that is passed between
            processes for efficient
            work distribution.
        first (int): Set to `True` when the walker is the first one to receive a
            work request from its peers, indicating that it should send out a work
            request to its neighbors.
        workrequest (MPIStatus): Used to track whether a node has requested work
            or not.
        items (deque): Used to store the files or directories encountered during
            the parallel walk process.
        results (MPI_Gathered): Initialized to gather results from other processes
            when the walker is done with its work.
        finished (bool): Used to indicate if the walker has completed its work or
            not.

    """
    def __init__(self, comm, results=None):
        """
        Initializes an object of the `ParallelWalk` class, setting its various
        attributes and behaviors based on input parameters.

        Args:
            comm (Dup): Used to represent a communication object that allows the
                worker class to communicate with other workers.
            results (NoneType): An optional argument that represents the initial
                results of the worker.

        """
        self.comm = comm.Dup()
        self.rank = self.comm.Get_rank()
        self.workers = self.comm.size
        self.others = range(0, self.rank) + range(self.rank+1, self.workers)
        self.nextworker = (self.rank + 1) % self.workers
        self.colour = "White"
        self.token = False
        self.first = True
        self.workrequest = False
        self.items = deque()
        self.results = results
        self.finished = False

    
    def ProcessDir(self, directoryname):
        """This method is a stub called for each directory the walker 
        encounters.  Extend it for your own needs.

        directoryname contains the name of the directory being processed.

        If you have data which you want to return to the rank 0 process, use the results
        attribute; this is MPI gathered when the walkers are done."""
        pass


    def ProcessFile(self, filename):
        """This method is a stub called for each directory the walker 
        encounters.  Extend it for your own needs.

        filename contains the name of the file being processed.

        If you have data which you want to return to the rank 0 process, use the results
        attribute; this is MPI gathered when the walkers are done."""
        pass

    def _CheckforRequests(self):
        """
        In the ParallelWalk class manages work requests, items, and tokens among
        processes in a parallel environment. It receives messages from other
        processes, checks their tags, and updates internal variables accordingly.

        """
        # tags
        # 0 = work request
        # 1 = work item
        # 2 = token
        # 3 = Shutdown message
        status = MPI.Status()
        while self.comm.Iprobe(source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG):
            request = self.comm.recv(source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG, 
                                status=status)
            source = status.source
            tag = status.tag

            if tag == 0:
                numitems = len(self.items)
                if numitems > 1:
                    split = random.randrange(1, numitems)
    #            or split list in half
    #                split = numitems / 2
                    senditems = list(self.items)[:split]
                    remainingitems = list(self.items)[split:]
                    self.items = deque(remainingitems)
                    self.comm.send(senditems, dest=source, tag=1)
                    if source < self.rank:
                        self.colour = "Black"
                else:
                    self.comm.send("NoWork", dest=source, tag=1)

            if tag == 1:
                self.mpirequest.wait()
                if request != "NoWork":
                    self.items.extendleft(request)
                self.workrequest = False

            if tag == 2:
                self.token = request

            if tag == 3:
                self.finished = True
        return()

    def _ProcessNode(self):
        """
        Pops an item from the class's items list, reads the file or directory at
        that location, and adds it to the class's items list if it is not a
        directory, or processes its contents recursively if it is a directory.

        """
        filename, filetype = self.items.pop()

        try:
            # If the filesystem supports readdir d_type, then we will know if the node is
            # a file or a directory without doing any extra work. If it does not, we have
            # to do a stat.
            if filetype == 0:
                s = safestat.safestat(filename)
                if stat.S_ISDIR(s.st_mode):
                    filetype = readdir.dirent.DT_DIR
                else:
                    filetype = readdir.dirent.DT_REG

            # If we a directory, enumerate its contents and add them to the list of nodes
            # to be processed.
            if filetype == readdir.dirent.DT_DIR:
                for node in readdir.readdir(filename):
                    if not node.d_name in (".",".."):
                        fullname = os.path.join(filename, node.d_name)
                        self.items.appendleft((fullname, node.d_type))
            # Call the processing functions on the directory or file.
                self.ProcessDir(filename)
            else:
                self.ProcessFile(filename)
        except OSError as error:
            print "cannot access `%s':" % filename,
            print os.strerror(error.errno)
        return()

    def _AskForWork(self):
        """
        Within the ParallelWalk class randomly selects one of the others, sends a
        message with the tag "Hungry" to that target, and sets the work request
        to True.

        """
        target = random.choice(self.others)
        self.mpirequest = self.comm.isend("Hungry", dest=target, tag=0)
        self.workrequest = True

    def _CheckForTermination(self):
        """
        In the ParallelWalk class checks for termination conditions, including
        when all workers have finished and when the rank is zero and the colour
        is white. It also updates the token and sends it to the next worker if necessary.

        """
        # single process case is special; we can terminate straight away.
        if self.workers == 1:
            self.finished = True
            return()
        # We are done when rank 0 is white and has a white token.
        if (self.rank == 0 and self.token == "White" and 
            self.colour == "White"):
            if self.first == True:
                self.first = False
            else:
                # Tell the other workers that they are done, and then quit.
                self._sendShutdown()            
                self.finished = True

        # If we have the token, set the process and token colours as then send
        # the token on to the next process.
        if self.token != False:
            if self.rank == 0:
                self.colour = "White"
                self.token = "White"
                self.comm.send(self.token, self.nextworker, tag=2)
                self.token = False
            else:
                if self.colour == "White":
                    self.comm.send(self.token, self.nextworker, tag=2)
                    self.token = False

                elif self.colour == "Black":
                    self.token = "Black"
                    self.colour = "White"
                    self.comm.send(self.token, self.nextworker, tag=2)
                    self.token = False

    def _sendShutdown(self):
        """
        Sends a message to all workers with the tag "Shutdown" and the destination
        id starting from 1, invoking the receiver's `comm.send()` method.

        """
        for dest in range(1, self.workers):
            self.comm.send("Shutdown", dest=dest, tag=3)

    def gatherResults(self):
        """
        In the `ParallelWalk` class receives an argument `data` from the parent
        class's `comm` attribute, and returns the gathered data after applying the
        `gather` method to it.

        Returns:
            list: A gather result from the communication object `comm`.

        """
        data = self.comm.gather(self.results, root=0)
        return(data)

    def _tidy(self):
        self.comm.Free()

    def Execute(self, seed):
        """
        In the `ParallelWalk` class takes a seed directory and initializes the
        rank-0 walker with it, while also allowing for multiple seeds to be taken.
        It then enters an iterative main loop where it checks for requests, processes
        nodes, and pings the worklist between nodes until termination is reached.
        Finally, it gathers results and tidies up.

        Args:
            seed (object): Used to initialize the rank-0 walker with a seed directory.

        Returns:
            object: Returned by its `gatherResults()` method after it has completed
            its execution.

        """
        # Initialize the rank0 walker with the seed directory.
        # TODO: Be able to take multiple seeds
        if self.rank == 0:
            self.items.append((seed, 4))
            self.token = "White"
        else:
            self.token = False

        # main loop
        # See if we have any pending communication requests.
        # If we have work, then do it, otherwise we ask our peers for some.

        while self.finished == False:
            self._CheckforRequests ()
            if len(self.items) > 0:
                self._ProcessNode()
            else:
                # We only want one request in-flight, otherwise we
                # ping-pong worklist between nodes.
                if self.workrequest == False:
                    self._AskForWork()
            # If we have no more work, we might be 
            if len(self.items) == 0:
                self._CheckForTermination()
        # Gather the summary data from other ranks and then exit.
        data = self.gatherResults()
        self._tidy()
        return(data)
