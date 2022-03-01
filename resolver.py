import sys
import time
import datetime
import dns
import dns.name
import dns.message
import dns.query
import dns.flags

DEBUG = False

root_servers = ['199.9.14.201', 
                '192.33.4.12', 
                '199.7.91.13', 
                '192.203.230.10', 
                '192.5.5.241', 
                '192.112.36.4' , 
                '198.97.190.53', 
                '192.36.148.17', 
                '192.58.128.30', 
                '193.0.14.129', 
                '199.7.83.42', 
                '202.12.27.33']

def main():
    # system arguments
    query_type = sys.argv[1]
    name_to_resolve = sys.argv[2]

    # query attributes
    domain = name_to_resolve
    qtype = query_type
    qtime = time.time()
    
    # resolve
    dns_resolve(domain, qtype, qtime)

def dns_resolve(domain, qtype, qtime, output=True):
    # qnames = tld, domain name, subdomains
    qnames = get_qnames(domain)
    number_of_qnames = len(qnames)

    qname = qnames[0]
    index = 1

    # root servers' loop
    for root_server in root_servers:
        # qnames' loop
        while(index < number_of_qnames+1):
            if(DEBUG):
                print("\n")

            query_response = dns_query(qname, qtype, root_server)

            # response received
            if (query_response != None):
                # response with no error
                if(query_response.rcode() == dns.rcode.NOERROR):
                    # answer found
                    if(len(query_response.answer) > 0):
                        if(query_response.flags & dns.flags.AA ==  dns.flags.AA):
                            for rdata in query_response.answer:
                                if(rdata.rdtype == dns.rdatatype.A or rdata.rdtype == dns.rdatatype.NS or rdata.rdtype == dns.rdatatype.MX):
                                    # output
                                    if(output):
                                        dns_output(query_response, qtime)
                                    return query_response
                                if(rdata.rdtype == dns.rdatatype.CNAME):
                                    if(qtype.lower() == 'NS'.lower() or qtype.lower() == 'MX'.lower()):
                                        # output
                                        if(output):
                                            dns_output(query_response, qtime)
                                        return query_response
                                    # output
                                    print(f"--- resolving CNAME {str(rdata[0].target)}")
                                    # resolve cname
                                    dns_resolve(str(rdata[0].target), qtype, qtime)
                                    return query_response
                    # no answer found
                    else:
                        # trying additional servers
                        if(len(query_response.additional) > 0):
                            for rdata in query_response.additional:
                                if(rdata.rdtype == dns.rdatatype.A):
                                    root_server = rdata[0].address
                                    print(f"<-- {qtype} of {qname} is {root_server}")
                                    if(index < number_of_qnames):
                                        qname = qnames[index] + "." + qname
                                        index += 1
                                        does_server_respond = dns_query(qname, qtype, root_server, False)
                                        # breaks out of the loop of additional servers, and continue the outer while loop
                                        if(does_server_respond != None):
                                            break
                                        # trying next additional server
                                        else:
                                            continue
                                    # trying new root_server for same qname (qname == full domain name)
                                    else:
                                        query_response = dns_query(qname, qtype, root_server)
                                        if(query_response != None):
                                            if(len(query_response.answer) > 0 and (qtype.lower() == 'NS'.lower() or qtype.lower() == 'MX'.lower())):
                                                # output
                                                if(output):
                                                    dns_output(query_response, qtime)
                                                return query_response
                                            if(len(query_response.answer) > 0):
                                                if(query_response.flags & dns.flags.AA ==  dns.flags.AA):
                                                    for rdata in query_response.answer:
                                                        if(rdata.rdtype == dns.rdatatype.CNAME):
                                                            if(qtype.lower() == 'NS'.lower() or qtype.lower() == 'MX'.lower()):
                                                                # output
                                                                if(output):
                                                                    dns_output(query_response, qtime)
                                                                return query_response
                                                            # output
                                                            print(f"--- resolving CNAME {str(rdata[0].target)}")
                                                            # resolve cname
                                                            query_response = dns_resolve(str(rdata[0].target), qtype, qtime)
                                                        if(rdata.rdtype == dns.rdatatype.A):
                                                            # output
                                                            if(output):
                                                                dns_output(query_response, qtime)
                                                            return query_response
                                            if(len(query_response.authority) > 0):
                                                for rdata in query_response.authority:
                                                    if(rdata.rdtype == dns.rdatatype.SOA):
                                                        # output
                                                        if(output):
                                                            dns_output(query_response, qtime)
                                                        return query_response
                                        # trying next additional server
                                        else:
                                            continue
                        # trying authoritative servers
                        else:
                            # qtype NS/MX
                            if(len(query_response.authority) > 0 and (qtype.lower() == 'NS'.lower() or qtype.lower() == 'MX'.lower())):
                                # output
                                if(output):
                                    dns_output(query_response, qtime)
                                return query_response

                            # others
                            if(len(query_response.authority) > 0):
                                for rdata in query_response.authority:
                                    if(rdata.rdtype == dns.rdatatype.SOA or rdata.rdtype == dns.rdatatype.NS):
                                        if(index < number_of_qnames):
                                            qname = qnames[index] + "." + qname
                                            index += 1
                                        query_response = dns_query(qname, qtype, root_server)
                                        if(query_response != None):
                                            for rdata1 in query_response.authority:
                                                if(rdata1.rdtype == dns.rdatatype.NS):
                                                    # resolve (internal/without output)
                                                    ns_response = dns_resolve(str(rdata1[0].target), qtype, qtime, False)
                                                    if(ns_response != None):
                                                        if(len(ns_response.answer) > 0):
                                                            for rdata2 in ns_response.answer:
                                                                if(rdata2.rdtype == dns.rdatatype.A):
                                                                    root_server = rdata2[0].address
                                                                    does_server_respond = dns_query(qname, qtype, root_server)
                                                                    if(does_server_respond != None):
                                                                        break
                                                                    else:
                                                                        continue
                                                            # output
                                                            print(f"<-- {qtype} of {qname} is {root_server}")
                                                            query_response = dns_query(qname, qtype, root_server)
                                                            # output
                                                            if(output):
                                                                dns_output(query_response, qtime)
                                                            return
                                                        else:
                                                            continue
                                                    else:
                                                        continue
                                        else:
                                            continue
            # no response received
            else:
                # output
                print ("<-- ERROR <no answer>")
                break
    # output
    print ("<-- ERROR <could not be resolved>")

def dns_query(qname, qtype, root_server, output=True):
    # output
    if(output):
        print(f"--> Contacting root ({root_server}) for {qtype} of {qname}")

    if (qtype.lower() == 'A'.lower()):
        request = dns.message.make_query(qname, dns.rdatatype.A)
    elif (qtype.lower() == 'NS'.lower()):
        request = dns.message.make_query(qname, dns.rdatatype.NS)
    elif (qtype.lower() == 'MX'.lower()):
        request = dns.message.make_query(qname, dns.rdatatype.MX)
    elif (qtype.lower() == 'CNAME'.lower()):
        request = dns.message.make_query(qname, dns.rdatatype.CNAME)
    else:
        # output
        print ("--- UNSUPPORTED QUERY TYPE <supports only a, ns, mx, cname>")
        exit()
    try:
        response = dns.query.udp(request, root_server, timeout = 3)
        if(DEBUG):
            print("***************************************************")
            print("---------------------------------------------------")
            print("QNAME")
            print("---------------------------------------------------")
            print(qname)
            print("RESPONSE")
            print("---------------------------------------------------")
            print(query_response)
            print("---------------------------------------------------")
            print("ANSWER")
            print("---------------------------------------------------")
            print(query_response.answer)
    except dns.exception.Timeout:
        # output
        print ("<-- ERROR <dns udp query timeout>")
        return None
    return response

def dns_output(response, qtime):
    if(DEBUG):
        return

    if(len(response.answer) > 0):
        print ("\nANSWER:")
        for rrset in response.answer:
            print (rrset)
    if(len(response.authority) > 0):
        print ("\nAUTHORITY:")
        for rrset in response.authority:
            print (rrset)

    print ("\nDelay       :", int(round((time.time() - qtime)*1000)), "ms")
    print ("Datetime    :", str(datetime.datetime.now()))

def get_qnames(domain):
    # removing '.' at the end of domain, if exists
    if (domain.endswith('.')):
        domain = domain[:-1]
    # splitting the domain into qnames
    qnames = domain.split(".")
    # reversing, to setup the hierarchy of qname resolving
    qnames.reverse()
    return qnames

if __name__ == '__main__':
    main()
