
class SampleClass:
    """
    Manages a name and a list of data, providing methods for calculating summary
    statistics and displaying information about the data.

    Attributes:
        name (str): Initialized to the name passed during initialization, serving
            as a unique identifier for the object.
        data (List[float]): Used to store the input data for statistical calculations.

    """
    def __init__(self, name, data):
        """
        Initializes an object by setting its `name` and `data` attributes to the
        input arguments provided during construction.

        Args:
            name (str): Used to assign a name to an instance of the class.
            data (object): Used to initialize the instance variables of the class
                with the given name.

        """
        self.name = name
        self.data = data

    def greet(self):
        return f"Hello, {self.name}! Welcome to our platform."

    def calculate_statistics(self):
        """
        Calculates and returns various statistical measures for a given dataset,
        including sum, count, mean, and median.

        Returns:
            Dict[str,float]: Composed of four statistical measures: sum, count,
            mean and median

        """
        if not self.data:
            return None

        data_sum = sum(self.data)
        data_count = len(self.data)
        mean = data_sum / data_count

        sorted_data = sorted(self.data)
        mid = data_count // 2
        if data_count % 2 == 0:
            median = (sorted_data[mid - 1] + sorted_data[mid]) / 2
        else:
            median = sorted_data[mid]

        return {
            "sum": data_sum,
            "count": data_count,
            "mean": mean,
            "median": median
        }

    def display_info(self):
        """
        Calculates and displays statistical information about the sample, including
        the count, mean, and median of the data, or simply "No data available" if
        no data is available.

        Returns:
            str: A string containing information about the data, including the
            name, count, mean, and median.

        """
        stats = self.calculate_statistics()
        if stats:
            info = (
                f"Name: {self.name}\n"
                f"Data Count: {stats['count']}\n"
                f"Mean: {stats['mean']:.2f}\n"
                f"Median: {stats['median']:.2f}\n"
            )
        else:
            info = f"Name: {self.name}\nNo data available."
        return info


def top_level_function(x, y):
    """
    Performs calculations and returns a dictionary with four values: `sum`,
    `product`, `status`, and `product_status`.

    Args:
        x (int|float): Used in the calculation of the sum and product results.
        y (int): Used in the nested `nested_function` function to compute the
            product of x and y.

    Returns:
        Dict[str,int]: A collection of four elements: sum, product, status and
        product_status. Each element contains an integer value.

    """
    def nested_function(a, b):
        return a * b

    sum_result = x + y
    product_result = nested_function(x, y)

    if sum_result > 10:
        status = "Sum is greater than 10."
    else:
        status = "Sum is 10 or less."

    if product_result % 2 == 0:
        product_status = "Product is even."
    else:
        product_status = "Product is odd."

    return {
        "sum": sum_result,
        "product": product_result,
        "status": status,
        "product_status": product_status
    }


def simple_function(message, repeat=1, uppercase=False):
    """
    Takes a message and an optional repeat and uppercase parameter, and returns
    the repeated message with the specified options applied.

    Args:
        message (str): Used to represent the original message that will be repeated
            and modified.
        repeat (int|float): 1 by default, allowing the user to call the function
            multiple times with different arguments by changing its value.
        uppercase (bool): Used to specify whether the returned message should be
            in upper case or not.

    Returns:
        str: A string containing the message repeated the specified number of times
        and with the specified formatting option.

    """
    repeated_message = (message + " ") * repeat
    final_message = repeated_message.strip()

    if uppercase:
        final_message = final_message.upper()

    return final_message


if __name__ == "__main__":
    sample_data = [10, 20, 30, 40, 50]
    sample = SampleClass("Alice", sample_data)
    
    print(sample.greet())
    print(sample.display_info())
    
    results = top_level_function(4, 5)
    for key, value in results.items():
        print(f"{key.capitalize()}: {value}")

    print(simple_function("This is a test.", repeat=3, uppercase=True))
