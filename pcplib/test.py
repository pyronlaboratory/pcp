
class SampleClass:
    def __init__(self, name, data):
        self.name = name
        self.data = data

    def greet(self):
        return f"Hello, {self.name}! Welcome to our platform."

    def calculate_statistics(self):
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
