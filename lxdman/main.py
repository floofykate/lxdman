import yaml
import sys
import os
import logging
import coloredlogs

# configuration
global testing
global firewall
testing = True
firewall = "ufw"


def sanitize_list(string_list):
    return filter(None, string_list.split("\n"))


def call_command(command):
    if not testing:
        logging.info(f"Running \"{command}\".")
        os.system(command)
    else:
        logging.info(
            f"Prevented \"{command}\" from being ran due to testing mode.")


class LXDContainer:
    def __init__(self, name, image, host, build, ufw, iptables, guest):
        self.name = name
        self.image = image
        self.host = host
        self.build = build
        self.ufw = ufw
        self.iptables = iptables
        self.guest = guest
        self.create()
        self.init_host()
        self.init_build()
        self.init_guest()
        self.init_firewall()
        self.farewell()

    def create(self):
        logging.info(
            f"Creating container \"{self.name}\" using the image \"{self.image}\".")
        call_command(f"lxc launch {self.image} {self.name}")

    def init_firewall(self):
        logging.info(f"Initialising firewall rules for \"{self.name}\".")
        if firewall == "ufw":
            self.run_commands(self.ufw)
        if firewall == "iptables":
            self.run_commands(self.iptables)

    def init_host(self):
        logging.info(
            f"Running commands on the host required for \"{self.name}\".")
        self.run_commands(self.host)
        logging.info(
            f"Commands on the host required for \"{self.name}\" have been run.")

    def init_guest(self):
        logging.info(f"Building shell script package for \"{self.name}\".")
        self.build_package()
        logging.info(f"Sending shell script package for \"{self.name}\".")
        self.send_package()
        logging.info(f"Shell script package for \"{self.name}\" sent.")

    def init_build(self):
        logging.info(f"Running build process for \"{self.name}\". ")
        self.run_commands(self.build)
        logging.info(f"Build process for \"{self.name}\" executed.")

    def run_commands(self, command_list):
        for command in command_list:
            command = command.replace("<cname>", self.name)
            call_command(command)

    def build_package(self,):
        logging.info(f"Building guest package: {self.name}-package.sh")
        with open(f"{self.name}-package.sh", "w") as package_file:
            package_file.write("\n".join(self.guest))
        logging.info(f"Built guest package: {self.name}-package.sh")

    def send_package(self):
        logging.info(f"Sending package to container '{self.name}'.")
        if not testing:
            call_command(
                f"lxc file push {self.name}-package.sh {self.name}:/root")
            call_command(f"lxc exec {self.name} /root/{self.name}-package.sh")

    def farewell(self):
        logging.info(f"Container \"{self.name}\" should now be configured.")


def help():
    print("# Help\n")
    print("* lxdman help - Displays this prompt.")
    print("* lxdman ingest <lxdfile.yaml> - Create and set up a container based upon the LXDFile specified.")


def ingest(filename):
    with open(filename, "r") as ingest_file:
        container_config = yaml.load(ingest_file, Loader=yaml.FullLoader)

    return LXDContainer(
        container_config["name"],
        container_config["image"],
        sanitize_list(container_config["host"]),
        sanitize_list(container_config["build"]),
        sanitize_list(container_config["ufw"]),
        sanitize_list(container_config["iptables"]),
        sanitize_list(container_config["guest"])
    )


def main():
    logging.basicConfig(level=logging.DEBUG, filemode="w")
    logFormatter = logging.Formatter(
        "[%(asctime)s - %(levelname)s] [%(filename)s:%(lineno)s - %(funcName)s() - %(threadName)s] %(message)s", "%Y-%m-%d %H:%M:%S")
    rootLogger = logging.getLogger()
    rootLogger.handlers = []
    fileHandler = logging.FileHandler("lxdman.log")
    fileHandler.setFormatter(logFormatter)
    rootLogger.addHandler(fileHandler)
    coloredlogs.install(
        level='DEBUG', fmt="[%(asctime)s - %(levelname)s] [%(filename)s:%(lineno)s - %(funcName)s() - %(threadName)s] %(message)s")
    arg_len = len(sys.argv)

    logging.info(f"Command: {' '.join(sys.argv)}")
    if testing:
        logging.info("Testing mode is on. Commands will not be executed.")

    if arg_len == 1:
        help()

    if arg_len == 2:
        if sys.argv[1] == "help":
            help()

    if arg_len == 3:
        if sys.argv[1] == "ingest":
            ingest(sys.argv[2])


if __name__ == "__main__":
    main()
