chrome.runtime.onInstalled.addListener(function() {
    chrome.contextMenus.create({
        "id": "KubespiderMenu",
        "title": "Send to Kubespider",
        "contexts": ["all"]
    });
});

function handleRequestSend(link, tab, server) {
    var dataSource = tab.url
    if (link != null) {
        dataSource = link;
    }

    var data = {"dataSource": dataSource, "path": ""};
    fetch(server + '/api/v1/download', {
        method: 'POST',
        mode: 'cors',
        headers: {
            "Content-type": "application/json",
        },
        body: JSON.stringify(data),
    })
    .then(response => {
        response.status == 200 ? console.log("Download OK") : console.log("Download error");
    })
    .catch(error => {
        console.log("Download error");
    })
}

chrome.contextMenus.onClicked.addListener(function(info, tab) {
    if (info.menuItemId == "KubespiderMenu") {  
        chrome.storage.sync.get('server', (res) => {
            if (typeof res.server === "undefined") {
                document.getElementById('server').value = "";
                return
            }
            handleRequestSend(info.linkUrl, tab, res.server);
        });
    }
})