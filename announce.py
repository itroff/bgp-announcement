#!/usr/bin/env python
# coding: utf-8

import logging.handlers
import os
import argparse
import time
import shutil
import csv
import traceback
import netaddr
import sys


# settings singleton
class Config:
    __instance = None
    def __init__ (self):
        self.last_modified = 0
        self.timeout = ""
        self.oldSet = set()

        self.path = os.getcwd() + "/"
        self.version = None
        self.filename = "net.txt"
        self.community = "65535"
        self.targetfile = self.path + self.filename
        # dict neighbors - nexthop
        self.neighbors = dict()
        self.neighbors["10.0.0.1"] = "10.1.1.3"
        self.neighbors["10.0.0.2"] = "10.1.1.4"
        self.neighbors["fdaa:1:1:1::3"] = "fdaa:1:1:1::1"

    @staticmethod
    def instance():
        if Config.__instance is None:
            Config.__instance = Config()
        return Config.__instance

msgfmt = '%(asctime)s  %(message)s'
datfmt='%Y-%m-%d %H:%M:%S'
logHandler = logging.handlers.TimedRotatingFileHandler(Config.instance().path + "/log.txt", when="midnight")
logFormatter = logging.Formatter(msgfmt, datefmt=datfmt)
logHandler.setFormatter(logFormatter)
logger = logging.getLogger('announce')
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)

# parse new file network.csv
def parse_file():
    # need copy file and processing it
    try:
        last_modified = os.path.getmtime(Config.instance().targetfile)
        newSet = set()
        if Config.instance().last_modified != last_modified:
            logger.info("new file detected")
            if Config.instance().version is None:
                vers = "temp_" + Config.instance().filename
            else:
                vers = "temp_" + Config.instance().version + Config.instance().filename
            shutil.copyfile(Config.instance().targetfile, Config.instance().path + vers)
            with open(Config.instance().path + vers, 'r') as csvfile:
                spamreader = csv.reader(csvfile, delimiter=';', quotechar='|')
                try:
                    for row in spamreader:
                        newSet.add(row[0])
                except Exception:
                    logger.error("%s" % traceback.format_exc())

            Config.instance().last_modified = last_modified
            os.remove(Config.instance().path + vers)
            return newSet
    except OSError as exc:
        logger.error("Exception: %s" % exc)

# compare old files net.txt and new
def diff_sources(newSet):
    setSub = Config.instance().oldSet - newSet
    setAdd = newSet - Config.instance().oldSet

    for elem in setSub:
        ip_sub = netaddr.IPNetwork(elem)
        if Config.instance().version is None or (int(ip_sub.version) == int(Config.instance().version)):
            send_msg(elem, "withdraw")

    for elem in setAdd:
        ip_sub = netaddr.IPNetwork(elem)
        if Config.instance().version is None or (int(ip_sub.version) == int(Config.instance().version)):
            send_msg(elem, "announce")
    Config.instance().oldSet = newSet

# send to exabgp
def send_msg(address, command):
    peer_nh = Config.instance().neighbors.iteritems()
    for key, value in peer_nh:
        str_send = str()
        ip_addr = netaddr.IPNetwork(address)
        ip_peer = netaddr.IPNetwork(key)
        if int(ip_addr.version) == int(ip_peer.version):
            if command == "announce":
                str_send = "neighbor " + key + " announce route " + address + " next-hop " + value + "\n"
            elif command == "withdraw":
                # special withdraw for ipv6
                if int(ip_addr.version) == 4:
                    str_send = "neighbor " + key + " withdraw route " + address + "\n"
                else:
                    str_send = "neighbor " + key + " withdraw route " + address + " next-hop ::\n"
            # send to exabgp through pipe
            sys.stdout.write(str_send)
            logger.info(str_send)
            sys.stdout.flush()


def main():
    logger.info("Start BGP announcer")
    arg_storage = argparse.ArgumentParser()
    arg_storage.add_argument('--version', nargs='?', help='version ip protocol')
    arguments = arg_storage.parse_args()
    if arguments.version is None:
        logger.info("use combined version v4 v6")
    Config.instance().version = arguments.version
    print Config.instance().path
    try:
        # read file every 1 sec, diff and announce & withdraw
        while True:
            newSet = parse_file()
            if newSet is not None:
                diff_sources(newSet)
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Keyboard Interrupt")
    except Exception as exc:
        logger.error("Exception: %s" % exc)

main()