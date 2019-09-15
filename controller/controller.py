import argparse
import os, sys, time
import grpc
from scapy.layers.inet import Ether

sys.path.append(
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                 'test/'))
import p4runtime_lib.bmv2
from p4runtime_lib.switch import ShutdownAllSwitchConnections
import p4runtime_lib.helper
from p4.v1 import p4runtime_pb2_grpc
from p4.v1 import p4runtime_pb2


def printGrpcError(e):
    print "gRPC Error:", e.details(),
    status_code = e.code()
    print "(%s)" % status_code.name,
    traceback = sys.exc_info()[2]
    print "[%s:%d]" % (traceback.tb_frame.f_code.co_filename, traceback.tb_lineno)

def writeInitRules(p4info_helper, ingress_sw, dst_eth_addr, dst_ip_addr, port):

    table_entry = p4info_helper.buildTableEntry(
        table_name="MyIngress.tb",
        match_fields={
            "hdr.ipv4.dstAddr": (dst_ip_addr, 32)
        },
        action_name="MyIngress.tb_action",
        action_params={
            "dstAddr": dst_eth_addr,
            "port": port,
        })
    ingress_sw.WriteTableEntry(table_entry)
    print("Installed ingress tunnel rule on %s" % ingress_sw.name)

def main(p4info_file_path, bmv2_file_path):
    # Instantiate a P4Runtime helper from the p4info file
    p4info_helper = p4runtime_lib.helper.P4InfoHelper(p4info_file_path)

    try:
        # Create a switch connection object for s1 and s2;
        # this is backed by a P4Runtime gRPC connection.
        # Also, dump all P4Runtime messages sent to switch to given txt files.
        s1 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s1',
            address='127.0.0.1:50051',
            device_id=0,
            proto_dump_file='logs/s1-p4runtime-requests.txt')
        s2 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s2',
            address='127.0.0.1:50052',
            device_id=1,
            proto_dump_file='logs/s2-p4runtime-requests.txt')

        # Send master arbitration update message to establish this controller as
        # master (required by P4Runtime before performing any other write operation)
        s1.MasterArbitrationUpdate()
        s2.MasterArbitrationUpdate()

        # Install the P4 program on the switches
        s1.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                       bmv2_json_file_path=bmv2_file_path)
        print("Installed P4 Program using SetForwardingPipelineConfig on s1")
        s2.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                       bmv2_json_file_path=bmv2_file_path)
        print("Installed P4 Program using SetForwardingPipelineConfig on s2")

        # Write the rules that tunnel traffic from h1 to h2
        writeInitRules(p4info_helper, ingress_sw=s1, dst_eth_addr="08:00:00:00:02:22", dst_ip_addr="10.0.2.2", port=64)
        writeInitRules(p4info_helper, ingress_sw=s1, dst_eth_addr="08:00:00:00:01:11", dst_ip_addr="10.0.1.1", port=1)

        # Write the rules that tunnel traffic from h2 to h1
        writeInitRules(p4info_helper, ingress_sw=s2, dst_eth_addr="08:00:00:00:01:11", dst_ip_addr="10.0.1.1", port=2)
        writeInitRules(p4info_helper, ingress_sw=s2, dst_eth_addr="08:00:00:00:02:22", dst_ip_addr="10.0.2.2", port=1)

        while 1:
            print('cap')
            for item in s1.stream_msg_resp:
                print(item)
                eth = Ether(item.packet.payload)
                # eth.dst = '08:00:00:00:02:33'
                eth.show()
                request = p4runtime_pb2.StreamMessageRequest()
                request.packet.payload = item.packet.payload
                s2.requests_stream.put(request)


            time.sleep(1)

    except KeyboardInterrupt:
        print(" Shutting down.")
    except grpc.RpcError as e:
        printGrpcError(e)

    ShutdownAllSwitchConnections()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='P4Runtime Controller')
    parser.add_argument('--p4info', help='p4info proto in text format from p4c',
                        type=str, action="store", required=True)
    parser.add_argument('--bmv2-json', help='BMv2 JSON file from p4c',
                        type=str, action="store", required=True)
    args = parser.parse_args()

    if not os.path.exists(args.p4info):
        parser.print_help()
        print("\np4info file not found: %s\nHave you run 'make'?" % args.p4info)
        parser.exit(1)
    if not os.path.exists(args.bmv2_json):
        parser.print_help()
        print("\nBMv2 JSON file not found: %s\nHave you run 'make'?" % args.bmv2_json)
        parser.exit(1)

    main(args.p4info, args.bmv2_json)