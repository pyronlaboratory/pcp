class Car:
    """
    Has methods for starting, driving and stopping a car. It keeps track of fuel
    level and displays relevant messages based on fuel level.

    Attributes:
        make (str): Set in the constructor through the parameter `make`. It
            represents the brand or make of the car.
        model (String): A unique identifier for the car's model.
        fuel_capacity (int): 0 by default, representing the maximum amount of fuel
            a car can hold.
        fuel_level (int): 0 by default, representing the current amount of fuel
            available for driving.

    """
    def __init__(self, make, model, fuel_capacity):
        """
        Sets the attributes of a `Car` object: `make`, `model`, and `fuel_capacity`.

        Args:
            make (str): Set to a specific value representing the car's make, such
                as Toyota or Honda.
            model (str): Assigned to the instance variable `model`.
            fuel_capacity (int): Used to represent the fuel capacity of the vehicle.

        """
        self.make = make
        self.model = model
        self.fuel_capacity = fuel_capacity
        self.fuel_level = 0
    
    def start(self):
        """
        Determines if the car can be started based on its fuel level and returns
        a message accordingly. If the fuel level is above zero, it returns a message
        indicating that the car has started. Otherwise, it returns a message
        instructing the user to add fuel.

        Returns:
            str: `{"{self.make} {self.model} started."}` when the fuel level is
            greater than zero, and a value of `“Cannot start. Add fuel.”` otherwise.

        """
        if self.fuel_level > 0:
            return f"{self.make} {self.model} started."
        else:
            return "Cannot start. Add fuel."

    def drive(self, distance):
        """
        Calculates how much fuel is needed to drive a certain distance based on
        the car's current fuel level and drives the distance if there is enough
        fuel, otherwise it returns an error message.

        Args:
            distance (int): Representing the distance to be driven by the vehicle.

        Returns:
            str: A message indicating whether the car can drive a given distance
            or not

        """
        if self.fuel_level > 0:
            fuel_needed = distance / 10  # Assuming fuel efficiency of 10 km per liter
            if fuel_needed <= self.fuel_level:
                self.fuel_level -= fuel_needed
                return f"{self.make} {self.model} drove {distance} kilometers."
            else:
                return "Not enough fuel to drive that far."
        else:
            return "Cannot drive. Add fuel."

    def stop(self):
        return f"{self.make} {self.model} stopped."

def calculate_efficiency(distance, fuel_used):
    """
    Calculates the fuel efficiency of a vehicle based on the distance traveled and
    the amount of fuel used, returning the result as a string with the fuel
    efficiency expressed in kilometers per liter.

    Args:
        distance (int): Representing the distance traveled by the vehicle.
        fuel_used (float): Used to calculate the fuel efficiency of a vehicle based
            on the distance traveled and the amount of fuel consumed.

    Returns:
        str: A string representing the fuel efficiency in km/liter format.

    """
    efficiency = distance / fuel_used
    return f"Fuel efficiency: {efficiency} km/liter"


if __name__ == "__main__":
    my_car = Car("Toyota", "Camry", fuel_capacity=50)
    print(my_car.start())  # Output: Toyota Camry started.
    print(my_car.drive(150))  # Output: Toyota Camry drove 150 kilometers.
    print(calculate_efficiency(150, 12))  # Output: Fuel efficiency: 12.5 km/liter
    print(my_car.stop())  # Output: Toyota Camry stopped.
