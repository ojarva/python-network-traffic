from pysnmp.entity.rfc3413.oneliner import cmdgen
import time

class InvalidReplyException(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return repr(self.msg)

class GetNetworkStats(object):
    FULL_FIELDS = ["ifDescr", "ifSpeed", "ifPhysAddress", "ifAdminStatus", "ifOperStatus", "ifLastChange", "ifInOctets", "ifInDiscards", "ifInErrors", "ifOutOctets", "ifOutDiscards", "ifOutErrors", "ifOutQLen"]
    FIELDS = ["ifDescr", "ifPhysAddress", "ifOperStatus", "ifInOctets", "ifOutOctets"]

    def __init__(self, hostname, port, community):
        self.cmdgen = cmdgen.CommandGenerator()
        self.hostname = hostname
        self.port = port
        self.community = community
        self.stats = {}

    def gen_variables(self, mibs):
        mib_list = []
        for mib in mibs:
            mib_list.append(cmdgen.MibVariable("IF-MIB", mib))
        return mib_list

    def get_stats(self):
        opts = [
          cmdgen.CommunityData(self.community, mpModel=0),
          cmdgen.UdpTransportTarget((self.hostname, self.port))
        ]
        opts += self.gen_variables(self.FIELDS)

        s = {"meta": {}, "entries": {}}
        errorIndication, errorStatus, errorIndex, varBindTable = self.cmdgen.nextCmd(
           *opts,
           lookupValues=True, lookupNames=True
        )
        s["meta"]["timestamp"] = time.time()

        if errorIndication:
            raise InvalidReplyException(errorIndication)

        if errorStatus:
            raise InvalidReplyException('%s at %s' % (
               errorStatus.prettyPrint(),
               errorIndex and varBindTable[-1][int(errorIndex)-1] or '?'
                )
            )

        for varBindTableRow in varBindTable:
            for name, val in varBindTableRow:
                pretty_name = name.prettyPrint().rsplit(".")
                pretty_val = val.prettyPrint().replace("'", "")
                try:
                    pretty_val = int(pretty_val)
                except ValueError:
                    pass
                interface_id = pretty_name[1].replace("\"", "")
                key_name = pretty_name[0].replace("IF-MIB::if", "")

                if interface_id not in s["entries"]:
                  s["entries"][interface_id] = {}

                s["entries"][interface_id][key_name] = pretty_val

        self.stats = s
        return s

class CalcStats(object):
    @classmethod
    def calc_octets(cls, octets1, octets2):
        if octets1 > octets2:
            # Wrapped around
            pass
            if octets1 < 2 ** 32:
                # 32-bit counter
                return 2 ** 32 - octets1 + octets2
            elif octets1 < 2 ** 64:
                # 64-bit counter
                return 2 ** 32 - octets1 + octets2
            else:
                raise ValueError("Invalid value for octets1: %s" % octets1)
        else:
            return octets2 - octets1

    def diff_stats(self, stats1, stats2):
        results = {}
        time_diff = stats2["meta"]["timestamp"] - stats1["meta"]["timestamp"]
        assert time_diff > 0
        for interface in stats1["entries"]:
            if interface not in stats2["entries"]:
                # Interface does not exist in second dataset
                continue
            if1 = stats1["entries"][interface]
            if2 = stats2["entries"][interface]
            # Detect wraparound
            in_data = self.calc_octets(if1["InOctets"], if2["InOctets"]) * 8 / time_diff
            out_data = self.calc_octets(if1["OutOctets"], if2["OutOctets"]) * 8 / time_diff

            results[interface] = {"status": if2["OperStatus"], "descr": if2["Descr"], "total_in": if2["InOctets"] / 8, "total_out": if2["OutOctets"] / 8, "mac": if2["PhysAddress"], "speed_in": in_data, "speed_out": out_data}
        return results
