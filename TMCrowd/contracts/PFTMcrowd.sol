// pragma solidity >=0.4.22 <=0.6.0;
pragma solidity ^0.5.16;
pragma experimental ABIEncoderV2;

contract write{
    bytes [] public access_policy;
    bytes [] public c1;
    bytes [] public c2;
    bytes [] public c3;
    mapping(bytes32 => bytes32) ETID_val;
    mapping(bytes32 => uint256) ETID_y;
    // mapping(bytes => uint) XSET;
    uint alpha;
    uint beta;
    mapping(uint => bytes []) public ST_w;
    bytes public pp = hex"90066455b5cfc38f9caa4a48b4281f292c260feef01fd61037e56258a7795a1c7ad46076982ce6bb956936c6ab4dcfe05e6784586940ca544b9b2140e1eb523f009d20a7e7880e4e5bfa690f1b9004a27811cd9904af70420eefd6ea11ef7da129f58835ff56b89faa637bc9ac2efaab903402229f491d8d3485261cd068699b6ba58a1ddbbef6db51e8fe34e8a78e542d7ba351c21ea8d8f1d29f5d5d15939487e27f4416b0ca632c59efd1b1eb66511a5a0fbf615b766c5862d0bd8a3fe7a0e0da0fb2fe1fcb19e8f9996a8ea0fccde538175238fc8b0ee6f29af7f642773ebe8cd5402415a01451a840476b2fceb0e388d30d4b376c37fe401c2a2c2f941dad179c540c1c8ce030d460c4d983be9ab0b20f69144c1ae13f9383ea1c08504fb0bf321503efe43488310dd8dc77ec5b8349b8bfe97c2c560ea878de87c11e3d597f1fea742d73eec7f37be43949ef1a0d15c3f3e3fc0a8335617055ac91328ec22b50fc15b941d3d1624cd88bc25f3e941fddc6200689581bfec416b4b2cb73";
    struct Set{
        bytes [] values;
        mapping(bytes => bool) is_in;
    }
    Set XSET;
    // 返回结果
    bytes32 [] public returnR_u;
    bytes [] public test_addr;
    uint code;
    bytes16 [] FF;
    bytes16 stag;

    function set_FF(bytes16 [] memory ff, uint len) public{
        for(uint i=0;i<len;++i){
            FF.push(ff[i]);
        }
    }

    function set_stag(bytes16 s) public{
        stag = s;
    }

    function random(uint number) public view returns(uint) {
    return uint(keccak256(abi.encodePacked(block.timestamp,block.difficulty,
        msg.sender))) % number;
    }

    function set_access_policy(bytes [] memory ap, uint len) public{
        for(uint i=0;i<len;++i){
            access_policy.push(ap[i]);
        }
    }

    function set_c1(bytes [] memory _c1, uint len) public{
        for(uint i=0;i<len;++i){
            c1.push(_c1[i]);
        }
    }

    function set_c2(bytes [] memory _c2, uint len) public{
        for(uint i=0;i<len;++i){
            c2.push(_c2[i]);
        }
    }

    function set_c3(bytes [] memory _c3, uint len) public{
        for(uint i=0;i<len;++i){
            c3.push(_c3[i]);
        }
    }

    function set_ETID_val(bytes32 [] memory addr, bytes32 [] memory val, uint len) public{
        for(uint i=0;i<len;++i){
            ETID_val[addr[i]] = val[i];
        }
    }

    function set_ETID_y(bytes32 [] memory addr, uint256 [] memory y, uint len) public{
        for(uint i=0;i<len;++i){
            ETID_y[addr[i]] = y[i];
        }
    }

    function XSET_add(bytes [] memory xtags, uint _len) public{
        for(uint i = 0; i < _len; i++){
            // bytes a = xtags[i];
            if(!XSET.is_in[xtags[i]]){
            XSET.values.push(xtags[i]);
            XSET.is_in[xtags[i]] = true;
            }
        }
    }

    function XSET_exist(bytes memory b) public view returns(bool){
        return XSET.is_in[b];
    }

    //function setP(bytes memory p) public{
    //    pp = p;
    //}

    function get_returnR_u() public view returns(bytes32 [] memory){
        return returnR_u;
    }

    function get_test_addr() public view returns(bytes [] memory){
        return test_addr;
    }

    function get_code() public view returns(uint){
        return code;
    }

    function set_ST_w(uint _c, bytes [] memory _searchtoken, uint _per_token_number) public{
        for(uint j = 0; j < _per_token_number; j++){
            // bytes m = _searchtoken[j];
            ST_w[_c].push(_searchtoken[j]);
        }
    }

    function expmod(bytes memory g, uint256 x, bytes memory p) public view returns ( bytes memory) {
        require(g.length == 384,"unqualified length of g");
        require(p.length == 384,"unqualified length of p");
        bytes memory input = abi.encodePacked(bytes32(g.length),abi.encode(0x20),bytes32(p.length),g,bytes32(x),p);
        bytes memory result = new bytes(384);
        bytes memory pointer = new bytes(384);
        assembly {
            // staticcall函数参数说明：gas消耗，调用外部函数地址，输入参数位置，长度，存储结果位置，存储长度
            if iszero(staticcall(sub(gas, 2000), 0x05, add(input,0x20), 0x380, add(pointer,0x20), 0x180 )) {
                revert(0, 0)
            }
        }
        for(uint i =0; i<12;i++) {
            bytes32 value;
            uint256 start = 32*i;
            assembly {
                value := mload(add(add(pointer,0x20),start))
            }
            for(uint j=0;j<32;j++) {
                result[start+j] = value[j];
            }
        }
        require(result.length == 384,"unqualified length of result");
        return result;
    }

    function concate(bytes16 _a, bytes16 _b, bytes memory _c, bytes memory _d) public view returns (bytes memory){
        return abi.encodePacked(_a, _b, _c, _d);
    }

    function toBytes(uint256 x) public returns (bytes memory b) {
        b = new bytes(32);
        assembly { mstore(add(b, 32), x) }
    }


    function TaskMatching(uint32 cnt_max,uint FF_len,uint n) public{
        // return ;
        //for(int i =0;i<25;++i){
        //    test_addr.push(ST_w[1][1]);
        //}
        // return ;
        code = 0;
        for(uint f=0;f<FF_len;++f){
        //  for(uint f=0;f<1;++f){
            for(uint i=1;i<=cnt_max;++i){
                // if(i == 4 )return ;
                // if(f == 2) return;
                bytes  memory i_tem = new bytes(15);
                // return ;
                // if(f == 1) return;
                bytes  memory b = toBytes(i);
                // return ;
                // if(f == 1) return;
                for(uint j=0;j<15;++j){
                    i_tem[14-j] = b[31-j];
                }
                // return ;
                // if(f == 1) return;
                bytes  memory delta0 = new bytes(1);
                delta0[0]=0x00;
                bytes memory concatenation1 = concate(stag, FF[f], i_tem, delta0);
                // test_addr.push(concatenation1);
                bytes32 addr = keccak256(abi.encodePacked(concatenation1));
                // test_addr.push(concatenation1);
                // return ;
                // if(f == 1) return;
                if(ETID_val[addr]!=bytes32(0)){
                    code =1;
                    // return ;
                    bytes32 val = ETID_val[addr];
                    uint256 y = ETID_y[addr];
                    uint match_cnt = 0;
                    for(uint j=1;j<n;++j){
                        bytes memory token_c_j = ST_w[i][j];
                        // return ;
                        // if (f==1 && i==3) return ;
                        //test_addr.push(token_c_j);
                        //test_addr.push(token_c_j);
                        // test_addr.push(token_c_j);
                        // if (f==1 && i==2) return ;
                        //bytes memory test_token_y;
                        //for(uint k=1;k<9;++k){
                        //    test_token_y = expmod(token_c_j, y, pp);
                        //}
                        bytes memory test_token_y = expmod(token_c_j, y, pp);
                        test_addr.push(test_token_y);
                        // if (f==1 && i==2) return ;
                        // if(f == 1) return;
                        // if(i == 3 )return ;
                        // return ;
                        if(XSET_exist(test_token_y)){
                            code = 2;
                            match_cnt = match_cnt +1;
                        }else{
                            break;
                        }
                        // return ;
                    }
                    // if(f == 1) return;
                    // if(i == 3 )return ;
                    // if (f==1 && i==3) return ;
                    // return ;
                    if(match_cnt == n-1){
                        // return ;
                        // if(f == 1) return;
                        // if(i == 3 )return ;
                        code = 2;
                        // return ;
                        // bytes1 delt = 0x01;
                        bytes  memory delta1 = new bytes(1);
                        delta1[0]=0x01;
                        bytes memory concatenation2 = concate(stag, FF[f], i_tem, delta1);
                        bytes32 msk = keccak256(abi.encodePacked(concatenation2));
                        bytes32 tid = val ^ msk;
                        returnR_u.push(tid);
                    }
                }else{
                    break;
                }
            }

        }
    }
}