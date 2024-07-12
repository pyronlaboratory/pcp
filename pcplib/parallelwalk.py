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
        Manages a parallel walk, where multiple processes work together to accomplish
        a task. It maintains a queue of items to be worked on and tracks the
        progress of each process through a color-based system.

        Attributes:
            self.comm (MPICommunicator): Used to store a copy of the MPI communicator
                for inter-process communication.
            self.rank (int): Initialized to be equal to the rank of the process
                creating the object, which is assigned by a communication module.
            self.workers (int): 0-based, representing the number of workers in a
                parallel walk simulation.
            self.others (List[int]): Defined as the union of the set of integers
                from 0 to the rank of the walker plus one, representing the IDs
                of workers other than the current walker.
            self.nextworker (int|str): Computed as (`rank + 1`) % `workers`. It
                determines the index of the next worker to be executed in the
                parallel walk.
            self.colour (str): Set to "White".
            self.token (bool): Set to False by default, indicating whether the
                current worker has finished its task or not.
            self.first (bool): Set to `True` when the object is created, indicating
                that this is the first worker in the parallel walk.
            self.workrequest (bool): Set to false by default, indicating whether
                or not the walker has requested work from other walkers.
            self.items (Deque[Any]): Used to store a queue of items to be processed
                in parallel by the worker processes.
            self.results (Union[None,List[str]]): Used to store the results returned
                by the workers during parallel walking.
            self.finished (bool): Set to `False` by default indicating that the
                walk has not completed yet.

        """
        def __init__(self, comm, results=None):
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
        Monitors for incoming work requests, sends items to other processes, and
        updates internal variables based on received tags.

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
        Pops an item from a list, determines the file type of the corresponding
        filename, and processes either the directory or file contents based on the
        file type.

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
        Sends a message "Hungry" to a random person in the group with the `comm`
        module, and sets `workrequest` to `True`.

        """
        target = random.choice(self.others)
        self.mpirequest = self.comm.isend("Hungry", dest=target, tag=0)
        self.workrequest = True

    def _CheckForTermination(self):
        """
        Checks if the process should terminate based on factors such as number of
        workers and color token. If termination is necessary, it sends a shutdown
        signal to the next worker and updates variables for further processing.

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
        Sends a message "Shutdown" to all workers except the current one using the
        `comm` object's `send()` method, with the `dest` parameter set to each
        worker's index starting from 1 and the `tag` parameter set to 3.

        """
        for dest in range(1, self.workers):
            self.comm.send("Shutdown", dest=dest, tag=3)

    def gatherResults(self):
        """
        Uses the `gather` method from the `comm` module to collect results from a
        distributed computation and returns them in a list.

        Args:
            self (GatherResults): Used to represent the current instance of a
                class, which contains the results that are being gathered.

        Returns:
            object: A result of gathering the results using the `comm.gather()` method.

        """
        data = self.comm.gather(self.results, root=0)
        return(data)

    def _tidy(self):
        self.comm.Free()

    def Execute(self, seed):
        """
        Executes a distributed algorithm by processing nodes, handling requests,
        and terminating when no more work is available.

        Args:
            self (Execute|rank0walker): Used to represent the current rank0 walker
                instance being executed.
            seed (str|int): Used to initialize the rank0 walker with the seed directory.

        Returns:
            object: Generated by the code inside its main loop.

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
