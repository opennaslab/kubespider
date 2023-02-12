// 这部分代码不要动 -- start
iB = {
    exports: {}
},
lB = {
    exports: {}
};

var g$ = {
    utf8: {
        stringToBytes: function(e) {
            return g$.bin.stringToBytes(unescape(encodeURIComponent(e)))
        },
        bytesToString: function(e) {
            return decodeURIComponent(escape(g$.bin.bytesToString(e)))
        }
    },
    bin: {
        stringToBytes: function(e) {
            for (var t = [], n = 0; n < e.length; n++) t.push(e.charCodeAt(n) & 255);
            return t
        },
        bytesToString: function(e) {
            for (var t = [], n = 0; n < e.length; n++) t.push(String.fromCharCode(e[n]));
            return t.join("")
        }
    }
},
_N = g$;

var e = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/",
t = {
    rotl: function(n, r) {
        return n << r | n >>> 32 - r
    },
    rotr: function(n, r) {
        return n << 32 - r | n >>> r
    },
    endian: function(n) {
        if (n.constructor == Number) return t.rotl(n, 8) & 16711935 | t.rotl(n, 24) & 4278255360;
        for (var r = 0; r < n.length; r++) n[r] = t.endian(n[r]);
        return n
    },
    randomBytes: function(n) {
        for (var r = []; n > 0; n--) r.push(Math.floor(Math.random() * 256));
            return r
    },
    bytesToWords: function(n) {
        for (var r = [], o = 0, a = 0; o < n.length; o++, a += 8) r[a >>> 5] |= n[o] << 24 - a % 32;
            return r
    },
    wordsToBytes: function(n) {
        for (var r = [], o = 0; o < n.length * 32; o += 8) r.push(n[o >>> 5] >>> 24 - o % 32 & 255);
            return r
    },
    bytesToHex: function(n) {
        for (var r = [], o = 0; o < n.length; o++) r.push((n[o] >>> 4).toString(16)), r.push((n[o] & 15).toString(16));
            return r.join("")
    },
    hexToBytes: function(n) {
        for (var r = [], o = 0; o < n.length; o += 2) r.push(parseInt(n.substr(o, 2), 16));
            return r
    },
    bytesToBase64: function(n) {
        for (var r = [], o = 0; o < n.length; o += 3)
            for (var a = n[o] << 16 | n[o + 1] << 8 | n[o + 2], i = 0; i < 4; i++) o * 8 + i * 6 <= n.length * 8 ? r.push(e.charAt(a >>> 6 * (3 - i) & 63)) : r.push("=");
                return r.join("")
    },
    base64ToBytes: function(n) {
        n = n.replace(/[^A-Z0-9+\/]/ig, "");
        for (var r = [], o = 0, a = 0; o < n.length; a = ++o % 4) a != 0 && r.push((e.indexOf(n.charAt(o - 1)) & Math.pow(2, -2 * a + 8) - 1) << a * 2 | e.indexOf(n.charAt(o)) >>> 6 - a * 2);
            return r
    }
};
lB.exports = t

var L8e = function(e) {
    return e != null && (sB(e) || D8e(e) || !!e._isBuffer)
};

function sB(e) {
    return !!e.constructor && typeof e.constructor.isBuffer == "function" && e.constructor.isBuffer(e)
}

function D8e(e) {
    return typeof e.readFloatLE == "function" && typeof e.slice == "function" && sB(e.slice(0, 0))
}

function GetTokenInternal(a, i) {
    var e = lB.exports,
    t = _N.utf8,
    n = L8e,
    r = _N.bin,
    o = function(a, i) {
        a.constructor == String ? i && i.encoding === "binary" ? a = r.stringToBytes(a) : a = t.stringToBytes(a) : n(a) ? a = Array.prototype.slice.call(a, 0) : !Array.isArray(a) && a.constructor !== Uint8Array && (a = a.toString());
        for (var l = e.bytesToWords(a), u = a.length * 8, s = 1732584193, d = -271733879, f = -1732584194, h = 271733878, v = 0; v < l.length; v++) l[v] = (l[v] << 8 | l[v] >>> 24) & 16711935 | (l[v] << 24 | l[v] >>> 8) & 4278255360;
        l[u >>> 5] |= 128 << u % 32, l[(u + 64 >>> 9 << 4) + 14] = u;
        for (var g = o._ff, w = o._gg, y = o._hh, b = o._ii, v = 0; v < l.length; v += 16) {
            var $ = s,
                S = d,
                _ = f,
                k = h;
            s = g(s, d, f, h, l[v + 0], 7, -680876936), h = g(h, s, d, f, l[v + 1], 12, -389564586), f = g(f, h, s, d, l[v + 2], 17, 606105819), d = g(d, f, h, s, l[v + 3], 22, -1044525330), s = g(s, d, f, h, l[v + 4], 7, -176418897), h = g(h, s, d, f, l[v + 5], 12, 1200080426), f = g(f, h, s, d, l[v + 6], 17, -1473231341), d = g(d, f, h, s, l[v + 7], 22, -45705983), s = g(s, d, f, h, l[v + 8], 7, 1770035416), h = g(h, s, d, f, l[v + 9], 12, -1958414417), f = g(f, h, s, d, l[v + 10], 17, -42063), d = g(d, f, h, s, l[v + 11], 22, -1990404162), s = g(s, d, f, h, l[v + 12], 7, 1804603682), h = g(h, s, d, f, l[v + 13], 12, -40341101), f = g(f, h, s, d, l[v + 14], 17, -1502002290), d = g(d, f, h, s, l[v + 15], 22, 1236535329), s = w(s, d, f, h, l[v + 1], 5, -165796510), h = w(h, s, d, f, l[v + 6], 9, -1069501632), f = w(f, h, s, d, l[v + 11], 14, 643717713), d = w(d, f, h, s, l[v + 0], 20, -373897302), s = w(s, d, f, h, l[v + 5], 5, -701558691), h = w(h, s, d, f, l[v + 10], 9, 38016083), f = w(f, h, s, d, l[v + 15], 14, -660478335), d = w(d, f, h, s, l[v + 4], 20, -405537848), s = w(s, d, f, h, l[v + 9], 5, 568446438), h = w(h, s, d, f, l[v + 14], 9, -1019803690), f = w(f, h, s, d, l[v + 3], 14, -187363961), d = w(d, f, h, s, l[v + 8], 20, 1163531501), s = w(s, d, f, h, l[v + 13], 5, -1444681467), h = w(h, s, d, f, l[v + 2], 9, -51403784), f = w(f, h, s, d, l[v + 7], 14, 1735328473), d = w(d, f, h, s, l[v + 12], 20, -1926607734), s = y(s, d, f, h, l[v + 5], 4, -378558), h = y(h, s, d, f, l[v + 8], 11, -2022574463), f = y(f, h, s, d, l[v + 11], 16, 1839030562), d = y(d, f, h, s, l[v + 14], 23, -35309556), s = y(s, d, f, h, l[v + 1], 4, -1530992060), h = y(h, s, d, f, l[v + 4], 11, 1272893353), f = y(f, h, s, d, l[v + 7], 16, -155497632), d = y(d, f, h, s, l[v + 10], 23, -1094730640), s = y(s, d, f, h, l[v + 13], 4, 681279174), h = y(h, s, d, f, l[v + 0], 11, -358537222), f = y(f, h, s, d, l[v + 3], 16, -722521979), d = y(d, f, h, s, l[v + 6], 23, 76029189), s = y(s, d, f, h, l[v + 9], 4, -640364487), h = y(h, s, d, f, l[v + 12], 11, -421815835), f = y(f, h, s, d, l[v + 15], 16, 530742520), d = y(d, f, h, s, l[v + 2], 23, -995338651), s = b(s, d, f, h, l[v + 0], 6, -198630844), h = b(h, s, d, f, l[v + 7], 10, 1126891415), f = b(f, h, s, d, l[v + 14], 15, -1416354905), d = b(d, f, h, s, l[v + 5], 21, -57434055), s = b(s, d, f, h, l[v + 12], 6, 1700485571), h = b(h, s, d, f, l[v + 3], 10, -1894986606), f = b(f, h, s, d, l[v + 10], 15, -1051523), d = b(d, f, h, s, l[v + 1], 21, -2054922799), s = b(s, d, f, h, l[v + 8], 6, 1873313359), h = b(h, s, d, f, l[v + 15], 10, -30611744), f = b(f, h, s, d, l[v + 6], 15, -1560198380), d = b(d, f, h, s, l[v + 13], 21, 1309151649), s = b(s, d, f, h, l[v + 4], 6, -145523070), h = b(h, s, d, f, l[v + 11], 10, -1120210379), f = b(f, h, s, d, l[v + 2], 15, 718787259), d = b(d, f, h, s, l[v + 9], 21, -343485551), s = s + $ >>> 0, d = d + S >>> 0, f = f + _ >>> 0, h = h + k >>> 0
        }
        return e.endian([s, d, f, h])
    };
    o._ff = function(a, i, l, u, s, d, f) {
    var h = a + (i & l | ~i & u) + (s >>> 0) + f;
    return (h << d | h >>> 32 - d) + i
    }, o._gg = function(a, i, l, u, s, d, f) {
    var h = a + (i & u | l & ~u) + (s >>> 0) + f;
    return (h << d | h >>> 32 - d) + i
    }, o._hh = function(a, i, l, u, s, d, f) {
    var h = a + (i ^ l ^ u) + (s >>> 0) + f;
    return (h << d | h >>> 32 - d) + i
    }, o._ii = function(a, i, l, u, s, d, f) {
    var h = a + (l ^ (i | ~u)) + (s >>> 0) + f;
    return (h << d | h >>> 32 - d) + i
    }, o._blocksize = 16, o._digestsize = 16, iB.exports = function(a, i) {
    if (a == null) throw new Error("Illegal argument " + a);
    var l = e.wordsToBytes(o(a, i));
    return i && i.asBytes ? l : i && i.asString ? r.bytesToString(l) : e.bytesToHex(l)
    }

    return iB.exports(a, i)
}
// 这部分代码不要动 -- end

// 这部分代码根据手册修改 -- start
function GetXunLeiToken(e) {
    return Q8e(e)
}

var R8e = GetTokenInternal
// 这部分代码根据手册修改 -- end


// 这部分代码从迅雷网站js脚本中拷贝 -- start
function Q8e(e) {
    return e + "." + R8e(e + x8e() + F8e() + B8e() + V8e() + z8e() + j8e() + H8e() + W8e() + U8e() + K8e() + q8e() + G8e() + Y8e() + X8e() + Z8e() + J8e())
}


function x8e() {
    return ""
}

function F8e() {
    return "lvmpxxflpbehvdrmafnjpjexoyggulwblebooxfuekhbrzakislubolbrjplrphhhkozgvvtkgsdgwkwnqwalnhypnjkpmztfvqnsatfadtagokpwzmhuqnxogaxotbhaonkrjnwygzosnkghdgnsbdknpklypxrqjepapducejnsggtleyxjpwkwfhdlgfaicuakvbblqipuzxgienqitzhtygweimdpyizjciqjfkrmrucezicztupumjervxesntflxqovujxqccafkgcbbjnpancfmvwahqygwjfntftzmvjuhfdovmsrpudrzcldoqpluzyziyeusuinpigxlszvziqhrlegmrgngipzqizeujkzkvvxrpbaaozijakiltykiawrckprdcjxcoowpfwlisrrlvdcvamxeomowhnbifydcguzlnwpxtradezkuhamowbftcvgdxuwrnmusuqyaxicrfdbxqumkjkqjdwakmqhukpvsjsaihjhaqvoldgyvbuoyhgxcuptmmqumyxnnskoxwfyzpabgijmjydgreoqowufvgcnobfbebkhlmqunggwqtkmaiiodytckbmamzsntcxvzwfdcwhszgdtyddbtnyprdonxwccavuoaybkclldzbxyatactxmmvbjfyntwykjtdtmjjipcvdynthitqvdreudrxyozatctthymsinraxrfksaqwttqzlchxiiohcpabbwvhgkwpohnexeyhkanhmwrsutdxtcrdbceqedwbvrhfltrmimvufprntsmuccrfewlvfbnncmjddejlhptsftzsxudsmteyffondhhxffwnyxbpflbguasfmkxbwanhabisqwybbhuplzhbtpyeplzxtdhgmdcrjtuywqhsqngpbhtldewouuaxukwsdoosaigllarvczliyxqtbqxbivoclkpqpfmkwijrtllzouiicseggepbliffzfaxuadjmdtqnuejezliirrohx"
}

function B8e() {
    return "lsdjsogxsihrzqlhwtlakyfnbavwwxxafjmtahknulwvfyeusjncatirnjgqtwrygxldbkvwvoywbzxtrcuvcugxwpatfofspxxdpgymfeieievdguaaqrdberqherpunypdbilheiujqobmvgntmpazuducjydggasjeapjjhzikftpjcuiktzgkesrredcszpdeinpknftomqest"
}

function V8e() {
    return "aaumxwaktqyzadrexgihtqmvcikuhqysmozyupxtxwlavyqurssjcapvrtukaiylhxevetqziazmtulqocpamefucghdvbknodtxyhxmdmjyrulvduriboqpqgjmsefezzshriassovdzcsdylnonbuprrwgijitatwcxxrqxzqiqipdjrnjjpvglzmanspsrcidmuczevmx"
}

function z8e() {
    return "duwsredjjdjywyaovrtjzzybfdwzeappiuvdcefwvwzgwxqrflmavfefpzwveemztoizwzpfpecmnvzzsubnmwqqmzfnuntfyvekmeltiqzahdgdatbbuifmininkzevspjgynzhxljxeucvmudetztdumeheyenhkuvntasuyejegnvbccyphdvzewyyhmqbvwanrfyebqhjjeyknvddabsbgbhdnolynkumsagprifdcpmuajcxjcnaoqtowndylhsvsedzhasnxujimoqf"
}

function j8e() {
    return "tqjgfsbjtefgkgqmofonkzedeecsgovvsvixznhfsofdsbbdwnpelhqwusndgmnsiopwbhwoolcfymloiwxzvywveseuhxqsoxcrkmrrqhjxksieyisbksfyqdurkabykrwdxvu"
}

function H8e() {
    return "nut"
}

function W8e() {
    return "cydyscbymlgzyposddxugjmruzrrtfhyaljwtizixvozfjsjeyzyvpje"
}

function U8e() {
    return "jjmsqhivp"
}

function K8e() {
    return "kndbxkanogsvncqbeiaypxhqnevdrmsygfvmwojvbqvgrxifh"
}

function q8e() {
    return "vhgrfrndrzsgiallapebszdcsmjsxr"
}

function G8e() {
    return "mgovybaiulwsovlmmkh"
}

function Y8e() {
    return "jpeatwpkxy"
}

function X8e() {
    return "grs"
}

function Z8e() {
    return "txscsv"
}

function J8e() {
    return "d"
}
// 这部分代码从迅雷网站js脚本中拷贝 -- end
