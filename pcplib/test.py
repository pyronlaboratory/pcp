
class SampleClass:
    """
    Has three methods: `__init__`, `greet`, and `calculate_statistics`. The
    `__init__` method initializes instance variables, while `greet` returns a
    personalized greeting. `calculate_statistics` computes and returns statistical
    information about the data.

    Attributes:
        name (str): Initialized in the `__init__` method with the parameter `name`.
            It stores the name value passed in the constructor.
        data (object): Initialized with a value passed to the `__init__` method.

    """
    def __init__(self, name, data):
        """
        Initializes an instance of the `SampleClass` by setting the `name` and
        `data` attributes to the input parameters passed during object creation.

        Args:
            name (str): Assigned to the attribute `name` upon initialization,
                storing the value provided by the caller.
            data (object): Used to initialize an instance variable named `data`.

        """
        self.name = name
        self.data = data

    def greet(self):
        return f"Hello, {self.name}! Welcome to our platform."

    def calculate_statistics(self):
        """
        Calculates various summary statistics (sum, count, mean, and median) for
        a list of values contained within an instance of the `SampleClass` object.

        Returns:
            dict: 4-element: sum, count, mean and median of an array or list data.

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
        Calculates and displays statistical information about a sample of data
        represented by an instance of `SampleClass`.

        Returns:
            str: A string containing information about the data, including name,
            count, mean, and median.

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
    Takes two arguments `x` and `y`, defines a nested function `nested_function`,
    calculates the sum and product of `x` and `y`, and returns a dictionary with
    four keys: `sum`, `product`, `status`, and `product_status`.

    Args:
        x (int): Passed as an argument to the nested `nested_function` function.
        y (int): Used in the calculation of the sum result.

    Returns:
        Python: A dictionary containing four key-value pairs: `sum`, `product`,
        `status`, and `product_status`.

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
    Takes a message and an optional repeat and uppercase parameter, repeats the
    message with the given repeat value, strips the resulting string, and returns
    it with the specified case if enabled.

    Args:
        message (str): Used to hold a string value that will be repeated and
            manipulated during the function's execution.
        repeat (int): Used to specify the number of times the passed message is
            concatenated with the space character before returning the final message.
        uppercase (bool): Used to determine if the final message should be made
            uppercase or not.

    Returns:
        str: A string that represents the concatenation of the input message and
        a specified repetition count, followed by stripping and possibly capitalizing
        the resulting string.

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
