class Car:
    """
    Has three methods: `__init__`, `start`, and `drive`. The `__init__` method
    initializes the object's attributes, while the `start` and `drive` methods
    allow the car to be started and driven a certain distance respectively, taking
    into account the current fuel level.

    Attributes:
        make (str): Initialized to the value "Make" during initialization.
        model (str): Initialized to a string value representing the car's model
            name at the time
            of object creation.
        fuel_capacity (int): Used to store the maximum amount of fuel that can be
            carried by the vehicle.
        fuel_level (int): 0 by default, representing the current amount of fuel
            in the vehicle's tank.

    """
    def __init__(self, make, model, fuel_capacity):
        """
        Sets instance variables "make", "model", and "fuel_capacity" for an object
        of class "Car". Initializing these variables to their respective values,
        the fuel level is set to 0.

        Args:
            make (str): Assigned to the instance attribute `make`.
            model (str): Assigned the value of `model`.
            fuel_capacity (int): Used to set the fuel capacity of the vehicle.

        """
        self.make = make
        self.model = model
        self.fuel_capacity = fuel_capacity
        self.fuel_level = 0
    
    def start(self):
        """
        Determines whether a `Car` can start based on its fuel level, and returns
        a message indicating if it can start or not to add fuel.

        Returns:
            str: "Can not start.Add fuel".

        """
        if self.fuel_level > 0:
            return f"{self.make} {self.model} started."
        else:
            return "Cannot start. Add fuel."

    def drive(self, distance):
        """
        Determines if a car can drive a certain distance based on its current fuel
        level, and if so, subtracts the required amount of fuel from the car's
        total fuel capacity before returning a message indicating the successful
        drive distance. If there is not enough fuel, it returns a message stating
        that the car cannot drive that far.

        Args:
            distance (int): The distance to be driven by the vehicle in kilometers.

        Returns:
            str: A message indicating whether the car can drive a certain distance
            based on its fuel level.

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
    the amount of fuel used.

    Args:
        distance (int): Representing the distance traveled by a vehicle.
        fuel_used (double): Representing the amount of fuel consumed by a vehicle
            during a given distance traveled, measured in liters.

    Returns:
        String: "Fuel efficiency: x km/liter" where x is the calculated efficiency
        ratio between distance and fuel used.

    """
    efficiency = distance / fuel_used
    return f"Fuel efficiency: {efficiency} km/liter"


if __name__ == "__main__":
    my_car = Car("Toyota", "Camry", fuel_capacity=50)
    print(my_car.start())  # Output: Toyota Camry started.
    print(my_car.drive(150))  # Output: Toyota Camry drove 150 kilometers.
    print(calculate_efficiency(150, 12))  # Output: Fuel efficiency: 12.5 km/liter
    print(my_car.stop())  # Output: Toyota Camry stopped.
