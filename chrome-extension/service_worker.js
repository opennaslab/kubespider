chrome.runtime.onInstalled.addListener(function () {
    chrome.contextMenus.create({
        "id": "KubespiderMenu",
        "title": "Send to Kubespider",
        "contexts": ["all"]
    });
});

function sleep(time) {
    return new Promise((resolve) => setTimeout(resolve, time));
}

function handleRequestSend(link, tab, server, token) {
    let dataSource = tab.url;
    if (link != null) {
        dataSource = link;
    }

    chrome.action.setBadgeText({text: 'GO'});
    let data = {"dataSource": dataSource, "path": ""};
    fetch(server + '/api/v1/download', {
        method: 'POST',
        mode: 'cors',
        headers: {
            "Content-type": "application/json",
            "Token": token,
        },
        body: JSON.stringify(data),
    }).then(response => {
        if (response.status === 200) {
            chrome.action.setBadgeText({text: 'OK'});
            sleep(9000).then(() => {
                chrome.action.setBadgeText({text: ''});
            });
        } else {
            chrome.action.setBadgeText({text: 'FAIL'});
            sleep(9000).then(() => {
                chrome.action.setBadgeText({text: ''});
            });
        }
    }).catch(error => {
        chrome.action.setBadgeText({text: 'FAIL'});
        sleep(9000).then(() => {
            chrome.action.setBadgeText({text: ''});
        });
    })
}

chrome.contextMenus.onClicked.addListener(function (info, tab) {
    if (info.menuItemId === "KubespiderMenu") {
        chrome.storage.sync.get(['server', 'token'], (res) => {
            if (!res.server) {
                document.getElementById('server').value = "";
                chrome.action.setBadgeText({text: 'FAIL'});
                sleep(9000).then(() => {
                    chrome.action.setBadgeText({text: ''});
                });
                return
            }
            handleRequestSend(info.linkUrl, tab, res.server, res.token);
        });
    }
})
