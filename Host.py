class Host:

    def __init__(self, name, host_id, description=""):
        self.host_id = host_id
        self.name = name
        self.description = description
        self.interfaces = []
        self.interface_dict = {}

    def add_interface(self, interface):
        self.interfaces.append(interface)
        self.interface_dict[interface.destination] = interface

    def __str__(self):

        output = f"#### Name: {self.name} ({self.host_id}) ####\n"

        for i in self.interfaces:
            output += str(i) + "\n"

        return output
