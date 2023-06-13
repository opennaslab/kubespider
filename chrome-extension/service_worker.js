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

async function badgeText(showText) {
    chrome.action.setBadgeText({text: showText});
    await sleep(9000);
    chrome.action.setBadgeText({text: ''});
}

async function handleRequestSend(linkUrl, tabUrl) {

    let dataSource = linkUrl;
    if (dataSource === "" || dataSource == null) {
        dataSource = tabUrl;
    }

    let {server, token, captureCookies} = await chrome.storage.sync.get(['server', 'token', 'captureCookies']);
    if (!server) {
        await badgeText('FAIL');
        return;
    }

    chrome.action.setBadgeText({text: 'GO'});

    let data = {"dataSource": dataSource, "path": ""};

    if (captureCookies) {
        let cookies = await chrome.cookies.getAll({url: tabUrl});
        data.cookies = cookies.map((cookie) => {
            return `${cookie.name}=${cookie.value}`;
        }).join(';');
    }

    try {
        console.log(JSON.stringify(data));
        let response = await fetch(server + '/api/v1/download', {
            method: 'POST',
            mode: 'cors',
            headers: {
                "Content-type": "application/json",
                "Authorization": `Bearer ${token}`,
            },
            body: JSON.stringify(data),
        });
        if (response.status === 200) {
            await badgeText('OK');
        } else {
            await badgeText('FAIL');
        }
    } catch (error) {
        await badgeText('FAIL');
    }
}

chrome.contextMenus.onClicked.addListener(function (info, tab) {
    if (info.menuItemId === "KubespiderMenu") {
        handleRequestSend(info.linkUrl, tab.url);
    }
});
