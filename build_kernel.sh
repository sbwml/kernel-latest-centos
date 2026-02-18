#!/bin/bash

# Check Linux Kernel Version
LATEST_VERSION=$(curl -s https://cdn.kernel.org/pub/linux/kernel/v6.x/sha256sums.asc | awk '{print $2}' | grep -E ^linux-6.18 | grep tar.xz | sed 's/linux-//g;s/.tar.xz//g' | tail -n 1)
if [ "$1" = "workflow_dispatch" ]; then
    NEW_VERSION=y
    echo $LATEST_VERSION > /VERSION
else
    TAGS=$(curl -sk https://api.github.com/repos/sbwml/kernel-latest-centos/tags | grep "name")
    if [[ "$TAGS" == *"$LATEST_VERSION"* ]]; then
        echo -e " \n\e[1;32mlinux-$LATEST_VERSION is already the latest lts version.\e[0m\n"
        exit 0
    else
        NEW_VERSION=y
        echo $LATEST_VERSION > /VERSION
    fi
fi

# Setting up the environment
yum install -y centos-release-scl-rh centos-release-scl
curl -s https://repo.cooluc.com/mailbox.repo > /etc/yum.repos.d/mailbox.repo
yum makecache
yum install -y \
  asciidoc \
  bc \
  bison \
  devtoolset-12-binutils \
  devtoolset-12-gcc \
  devtoolset-12-runtime \
  dwarves \
  elfutils-libelf-devel \
  gcc \
  gettext \
  hostname \
  libcap-devel \
  m4 \
  make \
  ncurses-devel \
  net-tools \
  newt-devel \
  openssl \
  openssl-devel \
  pciutils-devel \
  python3 \
  rpmdevtools \
  rsync \
  scl-utils \
  sed \
  tar \
  which \
  xmlto

# clang
source /etc/profile
export PATH="/opt/clang/bin:$PATH"

# Build Kernel
if [ $NEW_VERSION = y ]; then
    # goto root
    cd ~
    # spec
    DATE=$(date +"%a %b %d %Y")
    echo "* $DATE sbwml <admin@cooluc.com> - $LATEST_VERSION-1" >> kernel.spec
    echo "- Updated with the $LATEST_VERSION source tarball." >> kernel.spec
    echo "- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-$LATEST_VERSION]" >> kernel.spec
    sed -i "s/KERNEL_VERSION/$LATEST_VERSION/g" config
    sed -i "s/KERNEL_VERSION/$LATEST_VERSION/g" kernel.spec
    # src
    mkdir -pv rpmbuild/{BUILD,BUILDROOT,RPMS,SOURCES,SPECS,SRPMS}
    cp kernel.spec rpmbuild/SPECS/kernel-$LATEST_VERSION.spec
    cp config rpmbuild/SOURCES/config-$LATEST_VERSION-x86_64
    cp -a src/* rpmbuild/SOURCES/
    curl -L -k https://cdn.kernel.org/pub/linux/kernel/v6.x/linux-$LATEST_VERSION.tar.xz -o rpmbuild/SOURCES/linux-$LATEST_VERSION.tar.xz
    # build
    pushd ~/rpmbuild
        rpmbuild -ba SPECS/kernel-$LATEST_VERSION.spec
        if [ "$?" = 1 ]; then
            pushd BUILD/kernel-$LATEST_VERSION/linux-$LATEST_VERSION-*
                [ -f newoptions-el7-x86_64.txt ] && cat newoptions-el7-x86_64.txt >> .config
                . /opt/rh/devtoolset-12/enable
                make -s ARCH=x86_64 oldconfig LLVM=1 LLVM_IAS=1
                \cp .config ../../../SOURCES/config-$LATEST_VERSION-x86_64
            popd
            rpmbuild -ba SPECS/kernel-$LATEST_VERSION.spec
            [ "$?" = 1 ] && exit 1
        fi
        mkdir /rpm
        cp -a RPMS/x86_64/*.rpm /rpm
        cp -a SRPMS/*.rpm /rpm
        cp -a RPMS/x86_64 /x86_64
        cp -a SRPMS /SRPMS
    popd
    cd /
    tar zcvf rpm.tar.gz rpm
fi
