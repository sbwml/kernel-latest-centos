<div align="center">
<img src="https://github-production-user-asset-6210df.s3.amazonaws.com/16485166/263130623-3f9e5945-cc0c-44b9-b6fc-f9de2b8b9ce6.png" height="150.0px"/>
<h1 align="center">Linux 6.6 LTS Kernel for CentOS 7 / Red Hat 7</h1>
</div>

### Features:
- **Google's BBRv3 TCP congestion control.**
- **Linux Random Number Generator (LRNG v52).**
- **Enable eBPF support.**

### Install:

- **Add Repository & Update Kernel:**
  
  ```shell
  curl https://repo.cooluc.com/mailbox.repo > /etc/yum.repos.d/mailbox.repo
  yum makecache
  yum install kernel
  ```

- **Mount BPF sysfs (Optional):**
  
  ```shell
  curl https://repo.cooluc.com/kernel/files/sys-fs-bpf.mount > /etc/systemd/system/sys-fs-bpf.mount
  systemctl enable sys-fs-bpf.mount
  ```

- **Reboot:**

  ```shell
  reboot
  ```
