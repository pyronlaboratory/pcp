class Car:
    """
    Provides methods for starting, driving, and stopping a car. It tracks the fuel
    level and informs the user if there is not enough fuel to complete a drive.

    Attributes:
        make (str): Assigned to the constructor when initializing the object,
            representing the brand or manufacturer of the car.
        model (str): Representative of a car's model name.
        fuel_capacity (int): Used to store the maximum amount of fuel a car can
            hold, measured in units of the same as the `fuel_level` attribute.
        fuel_level (int|str): 0 by default, representing the current amount of
            fuel in the vehicle's tank.

    """
    def __init__(self, make, model, fuel_capacity):
        """
        Sets the make, model, and fuel capacity attributes and initializes the
        fuel level to 0.

        Args:
            make (str): Set to the vehicle's make.
            model (str): Defined as the model name for the vehicle.
            fuel_capacity (int): Representing the maximum amount of fuel that can
                be stored in the vehicle.

        """
        self.make = make
        self.model = model
        self.fuel_capacity = fuel_capacity
        self.fuel_level = 0
    
    def start(self):
        """
        Checks if the fuel level is above zero and then returns a message indicating
        that the car has started. If the fuel level is zero, it returns a message
        asking for more fuel to be added.

        Returns:
            str: A message indicating that the vehicle has started or an error
            message if there is no fuel left.

        """
        if self.fuel_level > 0:
            return f"{self.make} {self.model} started."
        else:
            return "Cannot start. Add fuel."

    def drive(self, distance):
        """
        Class calculates the amount of fuel needed to travel a given distance and
        checks if the current fuel level is sufficient. If not, it subtracts the
        necessary fuel from the current level and returns a message. Otherwise,
        it returns a message indicating that the distance can be driven.

        Args:
            distance (float): Used to represent the distance to be driven by the
                vehicle, which can range from 0 to any positive value.

        Returns:
            str: A message indicating whether the car can drive a certain distance
            or not.

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
    the amount of fuel used, returning the result in kilometers per liter.

    Args:
        distance (float): Representing the distance traveled by the vehicle during
            which the fuel consumption was measured.
        fuel_used (float): Used to represent the amount of fuel consumed by a
            vehicle during a given distance travelled.

    Returns:
        float: Fuel efficiency, measured in kilometers per liter.

    """
    efficiency = distance / fuel_used
    return f"Fuel efficiency: {efficiency} km/liter"


if __name__ == "__main__":
    my_car = Car("Toyota", "Camry", fuel_capacity=50)
    print(my_car.start())  # Output: Toyota Camry started.
    print(my_car.drive(150))  # Output: Toyota Camry drove 150 kilometers.
    print(calculate_efficiency(150, 12))  # Output: Fuel efficiency: 12.5 km/liter
    print(my_car.stop())  # Output: Toyota Camry stopped.
