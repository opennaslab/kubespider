chrome.runtime.onInstalled.addListener(function() {
    chrome.contextMenus.create({
        "id": "KubespiderMenu",
        "title": "Send to Kubespider",
        "contexts": ["all"]
    });
});

function handleRequestSend(link, tab) {
    var server = ""
    chrome.storage.sync.get('server', (res) => {
        if (res == null || res == "") {
            return
        }
        server = res.server
    });

    var dataSource = tab.url
    if (link != null) {
        dataSource = link
    }

    data = "{\"dataSource\":\"" + dataSource + "\",\"path\":\"\"}"
    fetch(server, {
        method: 'POST',
        mode: 'cors',
        headers: {
            "Content-type": "application/json",
        },
        body: JSON.stringify(data),
    })
    .then(response => {
        response.status == 200 ? console.log("Download OK") : console.log("Download error")
    })
    .catch(error => {
        console.log("Download error")
    })
}

chrome.contextMenus.onClicked.addListener(function(info, tab) {
    if (info.menuItemId == "KubespiderMenu") {
        handleRequestSend(info.linkUrl, tab)
    }
})