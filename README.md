# iterative-dns-resolver

A simple iterative version of DNS resolver, implemented using [python](https://www.python.org/), which understands the following query types: A, NS, MX, CNAME. 

The list of root servers that's been used by the program to iteratively resolve the domain names, is given [here](https://drive.google.com/file/d/1g5JkrceEIRb1czy1zWAJJpekJ1brVCKX/view?usp=sharing).

<br>

## Submitted By

S.M.Mehrabul Islam

Roll: N/A (Readmission) 

Lab #3 Write down a simple iterative version of DNS resolver. 

CSE-3111 (Computer Networking Lab)

1 March 2022

<br>

## Requirements

The following requirements must be fulfilled before using it on your system: 

- [python3](https://www.python.org/) must be installed on your system.

- [dnspython](https://www.dnspython.org/) must be installed on your system.

<br>

## How to Use

**1. Download**

You can download the code from [here](https://drive.google.com/file/d/1INB3-AG9E2s6_7yl2O4wxBEgnzG6PrMS/view?usp=sharing).

**2. Run**

(Make sure you are in the same directory as the soure code)

```
    python3 resolver.py <query_type>  <name_to_resolve>
```
For Example,

```
    python3 resolver.py A  www.google.com
```

**3. Output**

That should provide you with output formatted something like this:
```
--> Contacting root (199.9.14.201) for a of com
<-- a of com is 192.5.6.30
--> Contacting root (192.5.6.30) for a of google.com
<-- a of google.com is 216.239.34.10
--> Contacting root (216.239.34.10) for a of www.google.com

ANSWER:
www.google.com. 300 IN A 142.250.196.36

Delay       : 691 ms
Datetime    : 2022-03-01 20:58:06.607796
```

<br>

## Assumptions

- In case of multiple answers for a query, only the first answer is shown. 
- If the final DNS server returns a CNAME record, the program resolves the name of that CNAME record.
