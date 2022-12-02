---
title: kubespider specification
authors:
- "@jwcesign" # Authors' github accounts here.

creation-date: 2022-12-02

---

# Kubespider Specification
## Summary
kubespider is a unified downloading tool, it could be used to download anythings from any source, automatically or triggered. The most popular scenario must be downloading your favorite tv from somewhere. kubespider wants to involve the developers to adopt for different source/, like youtube.

## Motivation
Now nas/personal-server gets more and more popular, and they can be used to download things efficiently, like download the tv you like automatically when there comes new season. But it's quite complex to check and download from some website. So kubespider want to make this simple and fast with th nas/personal-server. Also kubespider will use the server to download to free your own working computer.

## Goals
1. Define a abstract layer to separate resource provider and kubespider-core.
2. Define the webhook api to receive downdload request.
3. Define the downdloading task type.
4. Define a abstract layer to separate kubespider-core and kubespider-download-provider.

## Non-Goals
none

## Proposal

### User Stories (Optional)

### Story 1
If using personal working laptop to download big file, it may take about whole day, which will stop our working because download always takes much cpu/ram. So with nas/personal-server, it could be very convenient to download the big file. Also, this should be simple enough to operate this.

### Story 2
Many people have the habit to binge-watched some tv. So with kubespider, it will download  automatically when the new season comes out.

### Notes/Constraints/Caveats (Optional)
none

## Design Details
### Architecture
![kubespider Architecture](../../images/kubespider-architecture.png)

The whole system contains: different source providers, kubespider-core, different download provider.

### Source Provider Type
In order to handle different downloading tasks, kubespider defines following provider type:
* period: Will run this provider periodically to download some tv when there is something new.(trigger or none-trigger)
* disposable: Will run this provider just one time when triggerd.

### Source File Type
In order to handle different resource downaloading, kubespider defines following file type:
* general: zip, msi, exe, etc. Or other file type kubespider can't recognize.
* torrent: torrent file.

### Resource Provider Abstract API
### Download Provider Abstract API
### Kubespider Webhook API