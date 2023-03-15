function sleep (time) {
    return new Promise((resolve) => setTimeout(resolve, time));
}

function sendRequest() {
    var dataSource = document.getElementById('url').value;
    var path = document.getElementById('path').value;
    var server = "";

    chrome.storage.sync.get('path', (res) => {
        if (res != path) {
            chrome.storage.sync.set({'path': path}, () => {
                console.log('path set successed!');
            });
        }
    });

    chrome.storage.sync.get('server', (res) => {
        if (typeof res.server === "undefined" || res.server == "") {
            document.getElementById('download').innerHTML = "Please set server";
            sleep(3000).then(() => {
                document.getElementById('download').innerHTML = "Download";
            });
        }
        if (dataSource == "" || dataSource == null) {
            return;
        }
        
        var data = {"dataSource": dataSource, "path": path};
        fetch(res.server + '/api/v1/download', {
            method: "POST",
            mode: "cors",
            headers: {
                "Content-type": "application/json",
            },
            body: JSON.stringify(data),
        })
        .then(response => {
            if (response.status == 200) {
                document.getElementById('download').innerHTML = "OK";
                sleep(3000).then(() => {
                    document.getElementById('url').value = "";
                    document.getElementById('download').innerHTML = "Download";
                });
            } else {
                document.getElementById('download').innerHTML = response.body;
                sleep(3000).then(() => {
                    document.getElementById('download').innerHTML = "Download";
                });
            }
        })
        .catch(error => {
            document.getElementById('download').innerHTML = error;
            sleep(3000).then(() => {
                document.getElementById('download').innerHTML = "Download";
            });
        });
    });
}

async function saveConfig() {
    const serverInput = document.getElementById('server');
    const serverValue = serverInput.value;
    const saveBtn = document.getElementById('save')

    saveBtn.classList.add('btn-loading');
    try {
        const response = await fetch(`${serverValue}/healthz`, {
          method: 'GET',
          mode: 'cors',
        });
    
        if (response.ok) {
            saveBtn.classList.remove('btn-loading');
            saveBtn.classList.add('btn-success');
            saveBtn.innerHTML = 'OK';
            await chrome.storage.sync.set({ server: serverValue });
            await sleep(3000);
            saveBtn.classList.remove('btn-success');
            saveBtn.innerHTML = 'Save';
        } else {
            saveBtn.classList.remove('btn-loading');
            saveBtn.classList.add('btn-danger');
            saveBtn.innerHTML = response.body;
            await sleep(3000);
            saveBtn.classList.remove('btn-danger');
            saveBtn.innerHTML = 'Save';
        }
    } catch (error) {
        saveBtn.classList.remove('btn-loading');
        saveBtn.classList.add('btn-danger');
        saveBtn.innerHTML = error;
        await sleep(3000);
        saveBtn.classList.remove('btn-danger');
        saveBtn.innerHTML = 'Save';
    }
}

function openGitHub() {
    chrome.tabs.create({ url: "https://github.com/jwcesign/kubespider" });
}

async function refreshDownload() {
    const refreshBtn = document.getElementById('refresh');
  
    const { server } = await chrome.storage.sync.get('server');
    if (!server) return;

    refreshBtn.classList.add('btn-loading');
    refreshBtn.innerHTML = 'Refreshing...';
    try {
        const response = await fetch(`${server}/api/v1/refresh`, {
            method: 'GET',
            mode: 'cors',
        });
  
        if (response.ok) {
            refreshBtn.classList.remove('btn-loading');
            refreshBtn.classList.add('btn-success');
            refreshBtn.innerHTML = 'OK';
            await sleep(3000);
            refreshBtn.classList.remove('btn-success');
            refreshBtn.innerHTML = 'Refresh';
        } else {
            refreshBtn.classList.remove('btn-loading');
            refreshBtn.classList.add('btn-danger');
            refreshBtn.innerHTML = response.body;
            await sleep(3000);
            refreshBtn.classList.remove('btn-danger');
            refreshBtn.innerHTML = 'Refresh';
        }
    } catch (error) {
        refreshBtn.classList.remove('btn-loading');
        refreshBtn.classList.add('btn-danger');
        refreshBtn.innerHTML = error;
        await sleep(3000);
        refreshBtn.classList.remove('btn-danger');
        refreshBtn.innerHTML = 'Refresh';
    }
}

chrome.storage.sync.get('server', (res) => {
    if (typeof res.server === "undefined" || res.server == "") {
        document.getElementById('server').value = "";
        return;
    }
    console.log(res.server);
    document.getElementById('server').value = res.server;
});

chrome.storage.sync.get('path', (res) => {
    if (typeof res.path === "undefined") {
        document.getElementById('path').value = "";
        return;
    }
    document.getElementById('path').value = res.path;
});

document.getElementById('download').addEventListener('click', sendRequest);
document.getElementById('save').addEventListener('click', saveConfig);
document.getElementById('openGitHub').addEventListener('click', openGitHub);
document.getElementById('refresh').addEventListener('click', refreshDownload);
