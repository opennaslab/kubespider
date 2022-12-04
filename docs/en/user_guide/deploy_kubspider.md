# Deploy with Docker

## Before Start
I strongly recommend you deploy kubespider with docker, it's easy and fast.
So you should install docker on your machine(personal-server or nas). Follow [official docs](https://docs.docker.com/engine/install/ubuntu/) to install it if you not.

### Run with default configuration
### Install motrix server and Kubespider
1. Clone repo and install
    ```
    git clone https://github.com/jwcesign/kubespider.git
    bash hack/install.sh
    ```
2. Start the motrix programe 
   Open your chrome(or other browser), and go to `http://<your_personal-server/nas_ip>:8081` and start motrix as follows:
    ![img](../../images/motrix-server-start.jpg)

### Following
1. Try download file: