## TMCrowd

### File Structure

```markdown
.
├── IWQOS2020															
│   ├── IWQOS_create.py
│   ├── app
│   │   └── IWQOS_build_index.py
│   ├── broker.txt
│   ├── broker_key.txt
│   ├── build
│   │   └── contracts
│   │       └── federated.json
│   ├── contracts
│   │   └── IWQOS.sol
│   ├── dataset_test					// test data(/dataset_test/requester/File_name)
│   │   ├── 111
│   │   │   ├── 1
│   │   │   ├── 2
│   │   │   └── 3
│   │   ├── 222
│   │   │   ├── 1
│   │   │   ├── 2
│   │   │   └── 3
│   │   ├── 333
│   │   │   ├── 1
│   │   │   ├── 2
│   │   │   └── 3
│   │   ├── 444
│   │   │   ├── 1
│   │   │   ├── 2
│   │   │   └── 3
│   │   ├── 555
│   │   │   ├── 1
│   │   │   ├── 2
│   │   │   └── 3
│   │   └── 666
│   │       ├── 1
│   │       ├── 2
│   │       └── 3
│   ├── truffle-box.json
│   └── truffle-config.js
├── TMCrowd																		// our scheme
│   ├── app
│   │   └── function.py												// local algorithm
│   ├── build
│   │   └── contracts
│   │       └── write.json
│   ├── contracts
│   │   └── PFTMcrowd.sol										  // smart contract
│   ├── dataset_test			 // test data(/dataset_test/requester/File_name)
│   │   ├── 111
│   │   │   ├── 1
│   │   │   ├── 2
│   │   │   └── 3
│   │   ├── 222
│   │   │   ├── 1
│   │   │   ├── 2
│   │   │   └── 3
│   │   └── 333
│   │       ├── 1
│   │       ├── 2
│   │       └── 3
│   ├── truffle-box.json											// truffle config file
│   └── truffle-config.js                     // truffle config file
└── tree.txt
```

### Baseline

ZHANG C, GUO Y, DU H, et al. PFcrowd: Privacy-Preserving and Federated Crowdsourcing Framework by Using Blockchain[C/OL]//2020 IEEE/ACM 28th International Symposium on Quality of Service (IWQoS), Hang Zhou, China. 2020.

### Prepare Environment

Processor Name: 8-Core Intel Core i9

Memory: 32 GB

System: macOS 14.3

Python 3.7 / Solitidy 0.5.16

### Building Procedure

```shell
ganache-cli -g 1 -l 9007199254740991 --db ./RDBlockchain -s 1234 -a 2
# Compile contracts
# open a new terminal tab 
truffle compile
# Run apps
cd app
# make sure ganache-cli has showen "Listening on 127.0.0.1:8545"
python3.6 function.py
```

### Contact

[yangxu@stu.xjtu.edu.cn](mailto:yangxu@stu.xjtu.edu.cn)

yuzhem@foxmail.com