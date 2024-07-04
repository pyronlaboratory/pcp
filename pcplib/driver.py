class Car:
    """
    Has methods for starting, driving and stopping a car. It also keeps track of
    the fuel level and provides messages based on the available fuel level.

    Attributes:
        make (str): Initialized with the value of the object's `make` parameter
            during its initialization.
        model (str): A variable representing the name of the car's model.
        fuel_capacity (int): 0 by default, representing the maximum amount of fuel
            that can be carried by the vehicle.
        fuel_level (int): Initialized to 0 when the object is created. It represents
            the amount of fuel remaining in the car.

    """
    def __init__(self, make, model, fuel_capacity):
        """
        Class sets instance variables 'make', 'model', and 'fuelCapacity' and
        initializes 'fuel level' to zero.

        Args:
            make (str): Assigned to instance variable `make`.
            model (str): Used to represent the name or identification of the
                specific vehicle model.
            fuel_capacity (int): Used to represent the maximum amount of fuel that
                can be stored in the vehicle's tank.

        """
        self.make = make
        self.model = model
        self.fuel_capacity = fuel_capacity
        self.fuel_level = 0
    
    def start(self):
        """
        Determines whether to allow the car to start based on the level of fuel
        remaining and returns appropriate messages depending on the outcome.

        Returns:
            str: A message indicating whether the vehicle can be started or not.

        """
        if self.fuel_level > 0:
            return f"{self.make} {self.model} started."
        else:
            return "Cannot start. Add fuel."

    def drive(self, distance):
        """
        Determines if the vehicle can travel distance based on available fuel
        level. If enough fuel, it subtracts the necessary amount and returns message
        of successful journey. Otherwise, it returns a message indicating insufficient
        fuel.

        Args:
            distance (int): Representing the distance to be driven by the vehicle.

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
    the amount of fuel used. It returns a string message indicating the fuel
    efficiency in kilometers per liter.

    Args:
        distance (int): Passed as the distance traveled by the vehicle, in kilometers.
        fuel_used (double): Representing the amount of fuel consumed by the vehicle
            during its journey, usually measured in liters.

    Returns:
        str: "Fuel efficiency: {efficiency} km/liter".

    """
    efficiency = distance / fuel_used
    return f"Fuel efficiency: {efficiency} km/liter"


if __name__ == "__main__":
    my_car = Car("Toyota", "Camry", fuel_capacity=50)
    print(my_car.start())  # Output: Toyota Camry started.
    print(my_car.drive(150))  # Output: Toyota Camry drove 150 kilometers.
    print(calculate_efficiency(150, 12))  # Output: Fuel efficiency: 12.5 km/liter
    print(my_car.stop())  # Output: Toyota Camry stopped.
