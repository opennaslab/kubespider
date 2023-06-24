chrome.runtime.onInstalled.addListener(function () {
    chrome.contextMenus.create({
        "id": "KubespiderMenu",
        "title": "Send to Kubespider",
        "contexts": ["all"]
    });
});

chrome.contextMenus.onClicked.addListener(function (info, tab) {
    if (info.menuItemId === "KubespiderMenu") {
        let dataSource = info.linkUrl
        if (dataSource === "" || dataSource == null) {
            dataSource = tab.url;
        }

        let itemId = uuidv4();
        chrome.scripting.executeScript({
            target: {tabId: tab.id},
            func: showTask,
            args: [itemId, dataSource],
        })

        handleRequestSend(dataSource).then(err => {
            chrome.scripting.executeScript({
                target: {tabId: tab.id},
                func: showResult,
                args: [itemId, err],
            })
        });
    }
});

function uuidv4() {
    return ([1e7]+-1e3+-4e3+-8e3+-1e11).replace(/[018]/g, c =>
      (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16)
    );
  }

function sleep(time) {
    return new Promise((resolve) => setTimeout(resolve, time));
}

async function badgeText(showText) {
    chrome.action.setBadgeText({text: showText});
    await sleep(9000);
    chrome.action.setBadgeText({text: ''});
}

async function handleRequestSend(dataSource) {
    let {server, token, captureCookies} = await chrome.storage.sync.get(['server', 'token', 'captureCookies']);
    if (!server) {
        badgeText('FAIL');
        return 'Internal error happened in Chrome';
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
            badgeText('OK');
            return '';
        } else {
            badgeText('FAIL');
            return response.text();
        }
    } catch (error) {
        badgeText('FAIL');
        return error.toString();
    }
}

function showTask(id, url) {
    var toastItem = document.createElement('div');
    toastItem.setAttribute('class', 'kubespider-toast');
    toastItem.setAttribute('id', id);

    // TODO: Make this code better
    toastItem.innerHTML = '<div class="kubespider-toast-header"> \
                            <svg class="kubespider-toast-color" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" preserveAspectRatio="xMidYMid slice" focusable="false"> \
                                <rect id="statecolor-' + id + '" width="100%" height="100%" fill="#007aff"></rect> \
                            </svg> \
                            <strong class="kubespider-toast-state" id="state-' + id + '">Starting...</strong> \
                           </div> \
                           <div class="kubespider-toast-body" id="info-' + id + '">' + url + '</div>'

    parentDOM = document.getElementById('kubespider-parent');
    parentDOM.appendChild(toastItem);
}

async function showResult(id, err) {
    // yellow color means success
    var statecolor = '#ffff00';
    if (err != "") {
        // red color means failed
        statecolor = '#ff0100';
    }

    var stateColor = document.getElementById('statecolor-'+id);
    stateColor.setAttribute('fill', statecolor);

    var state = document.getElementById('state-'+id);
    if (err != "") {
        state.textContent = 'Fail...';
        var info = document.getElementById('info-'+id);
        info.textContent = err;
    } else {
        state.textContent = 'Success...';
    }

    // wait 6s to let users see the information
    await new Promise((resolve) => setTimeout(resolve, 6000));

    var task = document.getElementById(id);
    parentDOM = document.getElementById('kubespider-parent');
    parentDOM.removeChild(task);
}
