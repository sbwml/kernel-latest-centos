# Explicity use python3 to avoid python byte compile errors.
%global __os_install_post    \
    /usr/lib/rpm/redhat/brp-compress \
    %{!?__debug_package:\
    /usr/lib/rpm/redhat/brp-strip %{__strip} \
    /usr/lib/rpm/redhat/brp-strip-comment-note %{__strip} %{__objdump} \
    } \
    /usr/lib/rpm/redhat/brp-strip-static-archive %{__strip} \
    /usr/lib/rpm/brp-python-bytecompile /usr/bin/python3 %{?_python_bytecompile_errors_terminate_build} \
    /usr/lib/rpm/redhat/brp-python-hardlink \
    %{!?__jar_repack:/usr/lib/rpm/redhat/brp-java-repack-jars} \
%{nil}

%global __spec_install_pre %{___build_pre}

# Define the version of the Linux Kernel Archive tarball.
%define LKAver KERNEL_VERSION

# Define the buildid, if required.
#define buildid .local

# The following build options are enabled by default.
# Use either --without <option> on your rpmbuild command line
# or force the values to 0, here, to disable them.

# kernel
%define with_default %{?_without_default: 0} %{?!_without_default: 1}
# kernel-doc
%define with_doc     %{?_without_doc:     0} %{?!_without_doc:     1}
# kernel-headers
%define with_headers %{?_without_headers: 0} %{?!_without_headers: 1}
# perf
%define with_perf    %{?_without_perf:    0} %{?!_without_perf:    1}
%define with_perf    0
# tools
%define with_tools   %{?_without_tools:   0} %{?!_without_tools:   1}

# These architectures install vdso/ directories.
%define vdso_arches x86_64

# Architecture defaults.
%define asmarch x86
%define buildarch %{_target_cpu}
%define hdrarch %{_target_cpu}

# Per-architecture tweaks.

%ifarch noarch
# Documentation only.
%define with_default 0
%define with_headers 0
%define with_perf 0
%define with_tools 0
%endif

%ifarch x86_64
# 64-bit kernel, headers, perf and tools.
%define with_doc 0
%endif

# Determine the sublevel number and set pkg_version.
%define sublevel %(echo %{LKAver} | %{__awk} -F\. '{ print $3 }')
%if "%{sublevel}" == ""
%define pkg_version %{LKAver}.0
%else
%define pkg_version %{LKAver}
%endif

# Set pkg_release.
%define pkg_release 1%{?dist}%{?buildid}

#
# Three sets of minimum package version requirements in the form of Conflicts.
#

#
# First the general kernel required versions, as per Documentation/Changes.
#
%define kernel_dot_org_conflicts ppp < 2.4.3-3, isdn4k-utils < 3.2-32, nfs-utils < 1.0.7-12, e2fsprogs < 1.37-4, util-linux < 2.12, jfsutils < 1.1.7-2, reiserfs-utils < 3.6.19-2, xfsprogs < 2.6.13-4, procps < 3.2.5-6.3, oprofile < 0.9.1-2, device-mapper-libs < 1.02.63-2, mdadm < 3.2.1-5

#
# Then a series of requirements that are distribution specific, either because
# the older versions have problems with the newer kernel or lack certain things
# that make integration in the distro harder than needed.
#
%define package_conflicts initscripts < 7.23, udev < 063-6, iptables < 1.3.2-1, ipw2200-firmware < 2.4, iwl4965-firmware < 228.57.2, selinux-policy-targeted < 1.25.3-14, squashfs-tools < 4.0, wireless-tools < 29-3

#
# We moved the drm include files into kernel-headers, make sure there's
# a recent enough libdrm-devel on the system that doesn't have those.
#
%define kernel_headers_conflicts libdrm-devel < 2.4.0-0.15

#
# Packages that need to be installed before the kernel because the %%post scripts make use of them.
#
%define kernel_prereq fileutils, module-init-tools >= 3.16-2, initscripts >= 8.11.1-1, grubby >= 8.28-2
%define initrd_prereq dracut >= 001-7

Name: kernel
Summary: The Linux kernel. (The core of any Linux-based operating system.)
Group: System Environment/Kernel
License: GPLv2
URL: https://www.kernel.org/
Version: %{pkg_version}
Release: %{pkg_release}
ExclusiveArch: noarch x86_64
ExclusiveOS: Linux
Provides: kernel = %{version}-%{release}
Provides: kernel-%{_target_cpu} = %{version}-%{release}
Provides: kernel-uname-r = %{version}-%{release}.%{_target_cpu}
Provides: kernel-drm = 4.3.0
Provides: kernel-drm-nouveau = 16
Provides: kernel-modeset = 1
Provides: %{name} = %{version}-%{release}
Provides: %{name}-%{_target_cpu} = %{version}-%{release}
Provides: %{name}-uname-r = %{version}-%{release}.%{_target_cpu}
Provides: %{name}-drm = 4.3.0
Provides: %{name}-drm-nouveau = 16
Provides: %{name}-modeset = 1
Requires(pre): %{kernel_prereq}
Requires(pre): %{initrd_prereq}
Requires(pre): linux-firmware >= 20100806-2
Requires(post): %{_sbindir}/new-kernel-pkg
Requires(preun): %{_sbindir}/new-kernel-pkg
Conflicts: %{kernel_dot_org_conflicts}
Conflicts: %{package_conflicts}
# We can't let RPM do the dependencies automatically because it'll then pick up
# a correct but undesirable perl dependency from the module headers which
# isn't required for the kernel proper to function.
AutoReq: no
AutoProv: yes

#
# List the packages used during the kernel build.
#
BuildRequires: devtoolset-12-gcc, devtoolset-12-binutils, devtoolset-12-runtime, scl-utils
BuildRequires: asciidoc, bash >= 2.03, bc, bison, binutils >= 2.12, diffutils
BuildRequires: elfutils-libelf-devel, findutils, gawk, gcc >= 3.4.2, gzip
BuildRequires: hostname, m4, make >= 3.78, module-init-tools, net-tools
BuildRequires: newt-devel, openssl, openssl-devel, patch >= 2.5.4, perl
BuildRequires: redhat-rpm-config >= 9.1.0-55, rsync, sh-utils, tar, xmlto, xz
BuildRequires: dwarves >= 1.16
%if %{with_perf}
BuildRequires: audit-libs-devel, binutils-devel, elfutils-devel, git
BuildRequires: java-1.8.0-openjdk-devel, libcap-devel, numactl-devel
BuildRequires: perl(ExtUtils::Embed), python-devel, python3
BuildRequires: slang-devel, xz-devel, zlib-devel
%endif
%if %{with_tools}
BuildRequires: gettext, libcap-devel, ncurses-devel, pciutils-devel
%endif

# Sources.
Source0: https://www.kernel.org/pub/linux/kernel/v6.x/linux-%{LKAver}.tar.xz
Source1: config-%{version}-x86_64
Source2: cpupower.service
Source3: cpupower.config

# Patches.
Patch0: 0001-backport-tcp_bbr3.patch
Patch1: 0002-add-lrng-v57.patch
Patch2: 0003-drivers-staging-add-tcp-brutal.patch
Patch3: 0004-modpost-remove-self-definitions-of-R_ARM_-macros.patch
Patch4: 0005-tools-power-x86-turbostat-add-reallocarray-function-.patch
Patch5: 991-mkbuild.patch

# Do not package the source tarball.
NoSource: 0

%description
This package provides the Linux kernel (vmlinuz), the core of any
Linux-based operating system. The kernel handles the basic functions
of the OS: memory allocation, process allocation, device I/O, etc.

%package devel
Summary: Development package for building kernel modules to match the kernel.
Group: System Environment/Kernel
Provides: kernel-devel = %{version}-%{release}
Provides: kernel-devel-%{_target_cpu} = %{version}-%{release}
Provides: kernel-devel-uname-r = %{version}-%{release}.%{_target_cpu}
Provides: %{name}-devel = %{version}-%{release}
Provides: %{name}-devel-%{_target_cpu} = %{version}-%{release}
Provides: %{name}-devel-uname-r = %{version}-%{release}.%{_target_cpu}
AutoReqProv: no
Requires(pre): %{_bindir}/find
Requires: perl
%description devel
This package provides the kernel header files and makefiles
sufficient to build modules against the kernel package.

%if %{with_doc}
%package doc
Summary: Various bits of documentation found in the kernel sources.
Group: Documentation
Provides: %{name}-doc = %{version}-%{release}
Provides: kernel-doc = %{version}-%{release}
Conflicts: kernel-doc < %{version}-%{release}
%description doc
This package provides documentation files from the kernel sources.
Various bits of information about the Linux kernel and the device
drivers shipped with it are documented in these files.

You'll want to install this package if you need a reference to the
options that can be passed to the kernel modules at load time.
%endif

%if %{with_headers}
%package headers
Summary: Header files of the kernel, for use by glibc.
Group: Development/System
Provides: glibc-kernheaders = 3.0-46
Obsoletes: glibc-kernheaders < 3.0-46
Provides: %{name}-headers = %{version}-%{release}
Provides: kernel-headers = %{version}-%{release}
Conflicts: kernel-headers < %{version}-%{release}
%description headers
This package provides the C header files that specify the interface
between the Linux kernel and userspace libraries and programs. The
header files define structures and constants that are needed when
building most standard programs. They are also required when
rebuilding the glibc package.
%endif

%if %{with_perf}
%package -n perf
Summary: Performance monitoring of the kernel.
Group: Development/System
License: GPLv2
%description -n perf
This package provides the perf tool and the supporting documentation
for performance monitoring of the Linux kernel.

%package -n python-perf
Summary: Python bindings for applications that will manipulate perf events.
Group: Development/Libraries
%description -n python-perf
This package provides a module that permits applications written in the
Python programming language to use the interface to manipulate perf events.

%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")}
%endif

%if %{with_tools}
%package -n %{name}-tools
Summary: Assortment of tools for the kernel.
Group: Development/System
License: GPLv2
Provides:  cpupowerutils = 1:009-0.6.p1
Obsoletes: cpupowerutils < 1:009-0.6.p1
Provides:  cpufreq-utils = 1:009-0.6.p1
Obsoletes: cpufreq-utils < 1:009-0.6.p1
Provides:  cpufrequtils = 1:009-0.6.p1
Obsoletes: cpufrequtils < 1:009-0.6.p1
Obsoletes: cpuspeed < 1:2.0
Requires: %{name}-tools-libs = %{version}-%{release}
Conflicts: kernel-tools < %{version}-%{release}
%description -n %{name}-tools
This package contains the tools/ directory and its supporting
documentation, derived from the kernel source.

%package -n %{name}-tools-libs
Summary: Libraries for the kernel tools.
Group: Development/System
License: GPLv2
Conflicts: kernel-tools-libs < %{version}-%{release}
%description -n %{name}-tools-libs
This package contains the libraries built from the
tools/ directory, derived from the kernel source.

%package -n %{name}-tools-libs-devel
Summary: Development package for the kernel tools libraries.
Group: Development/System
License: GPLv2
Requires: %{name}-tools = %{version}-%{release}
Requires: %{name}-tools-libs = %{version}-%{release}
Provides:  cpupowerutils-devel = 1:009-0.6.p1
Obsoletes: cpupowerutils-devel < 1:009-0.6.p1
Provides: %{name}-tools-devel
Conflicts: kernel-tools-libs-devel < %{version}-%{release}
%description -n %{name}-tools-libs-devel
This package contains the development files for the tools/ directory
libraries, derived from the kernel source.
%endif

# Disable the building of the debug package(s).
%define debug_package %{nil}

%prep
. /opt/rh/devtoolset-12/enable
export LLVM=1 LLVM_IAS=1 CC=clang

%setup -q -n %{name}-%{version} -c
%{__mv} linux-%{LKAver} linux-%{version}-%{release}.%{_target_cpu}

pushd linux-%{version}-%{release}.%{_target_cpu} > /dev/null

%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1

# Purge the source tree of all unrequired dot-files.
%{_bindir}/find -name '.*' -type f | %{_bindir}/xargs --no-run-if-empty %{__rm} -rf

%{__cp} %{SOURCE1} .

# Run make listnewconfig over all the configuration files.
%ifarch x86_64
for C in config-*-%{_target_cpu}*
do
    %{__cp} $C .config
    %{__make} -s ARCH=%{buildarch} listnewconfig | %{_bindir}/grep -E '^CONFIG_' > newoptions-el7-%{_target_cpu}.txt || true
    if [ -s newoptions-el7-%{_target_cpu}.txt ]; then
        cat newoptions-el7-%{_target_cpu}.txt
        exit 1
    fi
    %{__rm} -f newoptions-el7-%{_target_cpu}.txt
done
%endif

popd > /dev/null

%build
. /opt/rh/devtoolset-12/enable
export LLVM=1 LLVM_IAS=1 CC=clang

BuildKernel() {
    Flavour=$1

    %{__make} -s distclean

    # Select the correct flavour configuration file.
    if [ -z "${Flavour}" ]; then
        %{__cp} config-%{version}-%{_target_cpu} .config
    else
        %{__cp} config-%{version}-%{_target_cpu}-${Flavour} .config
    fi

    %define KVRFA %{version}-%{release}${Flavour}.%{_target_cpu}

    # Set the EXTRAVERSION string in the top level Makefile.
    %{__sed} -i "s/^EXTRAVERSION.*/EXTRAVERSION = -%{release}${Flavour}.%{_target_cpu}/" Makefile

    %{__make} -s ARCH=%{buildarch} oldconfig

    %{__make} -s ARCH=%{buildarch} %{?_smp_mflags} bzImage

    %{__make} -s ARCH=%{buildarch} %{?_smp_mflags} modules

    # Install the results into the RPM_BUILD_ROOT directory.
    %{__mkdir_p} $RPM_BUILD_ROOT/boot
    %{__install} -m 644 .config $RPM_BUILD_ROOT/boot/config-%{KVRFA}
    %{__install} -m 644 System.map $RPM_BUILD_ROOT/boot/System.map-%{KVRFA}

    # We estimate the size of the initramfs because rpm needs to take this size
    # into consideration when performing disk space calculations. (See bz #530778)
    dd if=/dev/zero of=$RPM_BUILD_ROOT/boot/initramfs-%{KVRFA}.img bs=1M count=20

    %{__cp} arch/x86/boot/bzImage $RPM_BUILD_ROOT/boot/vmlinuz-%{KVRFA}
    %{__chmod} 755 $RPM_BUILD_ROOT/boot/vmlinuz-%{KVRFA}

    %{__mkdir_p} $RPM_BUILD_ROOT/lib/modules/%{KVRFA}
    %{__mkdir_p} $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/kernel
    # Override $(mod-fw) because we don't want it to install any firmware.
    # We'll get it from the linux-firmware package and we don't want conflicts.
    %{__make} -s ARCH=%{buildarch} INSTALL_MOD_PATH=$RPM_BUILD_ROOT KERNELRELEASE=%{KVRFA} modules_install mod-fw=

%ifarch %{vdso_arches}
    %{__make} -s ARCH=%{buildarch} INSTALL_MOD_PATH=$RPM_BUILD_ROOT KERNELRELEASE=%{KVRFA} vdso_install
    %{_bindir}/find $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/vdso -name 'vdso*.so' -type f | \
        %{_bindir}/xargs --no-run-if-empty %{__strip}
    if %{_bindir}/grep -q '^CONFIG_XEN=y$' .config; then
        echo > ldconfig-%{name}.conf "\
# This directive teaches ldconfig to search in nosegneg subdirectories
# and cache the DSOs there with extra bit 1 set in their hwcap match
# fields.  In Xen guest kernels, the vDSO tells the dynamic linker to
# search in nosegneg subdirectories and to match this extra hwcap bit
# in the ld.so.cache file.
hwcap 1 nosegneg"
    fi
    if [ ! -s ldconfig-%{name}.conf ]; then
        echo > ldconfig-%{name}.conf "\
# Placeholder file, no vDSO hwcap entries used in this kernel."
    fi
    %{__install} -D -m 444 ldconfig-%{name}.conf $RPM_BUILD_ROOT/etc/ld.so.conf.d/%{name}-%{KVRFA}.conf
%endif

    # Save the headers/makefiles, etc, for building modules against.
    #
    # This looks scary but the end result is supposed to be:
    #
    # - all arch relevant include/ files
    # - all Makefile and Kconfig files
    # - all script/ files
    #
    %{__rm} -f $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build
    %{__rm} -f $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/source
    %{__mkdir_p} $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build
    pushd $RPM_BUILD_ROOT/lib/modules/%{KVRFA} > /dev/null
    %{__ln_s} build source
    popd > /dev/null
    %{__mkdir_p} $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/extra
    %{__mkdir_p} $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/updates
    %{__mkdir_p} $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/weak-updates

    # First copy everything . . .
    %{__cp} --parents `%{_bindir}/find  -name 'Makefile*' -o -name 'Kconfig*' -type f` $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build
    %{__cp} Module.symvers $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build
    %{__cp} System.map $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build
    if [ -s Module.markers ]; then
        %{__cp} Module.markers $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build
    fi

    %{__gzip} -c9 < Module.symvers > $RPM_BUILD_ROOT/boot/symvers-%{KVRFA}.gz

    # . . . then drop all but the needed Makefiles and Kconfig files.
    %{__rm} -rf $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/Documentation
    %{__rm} -rf $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/scripts
    %{__rm} -rf $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/include
    %{__cp} .config $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build
    %{__cp} -a scripts $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build
    if [ -d arch/%{buildarch}/scripts ]; then
        %{__cp} -a arch/%{buildarch}/scripts $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/arch/%{_arch} || :
    fi
    if [ -f arch/%{buildarch}/*lds ]; then
        %{__cp} -a arch/%{buildarch}/*lds $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/arch/%{_arch}/ || :
    fi
    %{__rm} -f $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/scripts/*.o
    %{__rm} -f $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/scripts/*/*.o
    if [ -d arch/%{asmarch}/include ]; then
        %{__cp} -a --parents arch/%{asmarch}/include $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/
    fi
    if [ -d arch/%{asmarch}/syscalls ]; then
        %{__cp} -a --parents arch/%{asmarch}/syscalls $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/
    fi
    %{__mkdir_p} $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/include
    pushd include > /dev/null
    %{__cp} -a * $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/include/
    popd > /dev/null
    %{__rm} -f $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/include/Kbuild

    # Ensure that objtool is present if CONFIG_STACK_VALIDATION is set.
    if %{_bindir}/grep -q '^CONFIG_STACK_VALIDATION=y$' .config; then
        %{__mkdir_p} $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/tools/objtool
        %{__cp} -a tools/objtool/objtool $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/tools/objtool
    fi

    # Copy the generated autoconf.h file to the include/linux/ directory.
    %{__cp} include/generated/autoconf.h $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/include/linux/

    # Now ensure that the Makefile, .config, auto.conf, autoconf.h and version.h files
    # all have matching timestamps so that external modules can be built.
    %{_bindir}/touch -r $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/Makefile \
        $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/.config \
        $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/include/config/auto.conf \
        $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/include/linux/autoconf.h \
        $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/include/generated/autoconf.h \
        $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/include/generated/uapi/linux/version.h

    # Remove any 'left-over' .cmd files.
    %{_bindir}/find $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build -name '*.cmd' -type f | \
        %{_bindir}/xargs --no-run-if-empty %{__rm} -f

    %{_bindir}/find $RPM_BUILD_ROOT/lib/modules/%{KVRFA} -name '*.ko' -type f > modnames

    # Mark the modules executable, so that strip-to-file can strip them.
    %{_bindir}/xargs --no-run-if-empty %{__chmod} u+x < modnames

    # Generate a list of modules for block and networking.
    %{_bindir}/grep -F /drivers/ modnames | %{_bindir}/xargs --no-run-if-empty nm -upA \
        | sed -n 's,^.*/\([^/]*\.ko\):  *U \(.*\)$,\1 \2,p' > drivers.undef

    collect_modules_list()
    {
        sed -r -n -e "s/^([^ ]+) \\.?($2)\$/\\1/p" drivers.undef | LC_ALL=C sort -u > $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/modules.$1
        if [ ! -z "$3" ]; then
            sed -r -e "/^($3)\$/d" -i $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/modules.$1
        fi
    }

    collect_modules_list networking \
        'register_netdev|ieee80211_register_hw|usbnet_probe|phy_driver_register|rt2x00(pci|usb)_probe|register_netdevice'

    collect_modules_list block \
        'ata_scsi_ioctl|scsi_add_host|scsi_add_host_with_dma|blk_alloc_queue|blk_init_queue|register_mtd_blktrans|scsi_esp_register|scsi_register_device_handler|blk_queue_physical_block_size|pktcdvd.ko|dm-mod.ko'

    collect_modules_list drm \
        'drm_open|drm_init'

    collect_modules_list modesetting \
        'drm_crtc_init'

    # Detect any missing or incorrect license tags.
    %{__rm} -f modinfo

    while read i
    do
        echo -n "${i#$RPM_BUILD_ROOT/lib/modules/%{KVRFA}/} " >> modinfo
        %{_sbindir}/modinfo -l $i >> modinfo
    done < modnames

    %{_bindir}/grep -E -v 'GPL( v2)?$|Dual BSD/GPL$|Dual MPL/GPL$|GPL and additional rights$' modinfo && exit 1

    %{__rm} -f modinfo modnames

    # Remove all the files that will be auto generated by depmod at the kernel install time.
    for i in alias alias.bin builtin.bin ccwmap dep dep.bin devname ieee1394map inputmap isapnpmap ofmap pcimap seriomap softdep symbols symbols.bin usbmap
    do
        %{__rm} -f $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/modules.$i
    done

    # Move the development files out of the /lib/modules/ file system.
    %{__mkdir_p} $RPM_BUILD_ROOT/usr/src/kernels
    %{__mv} $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build $RPM_BUILD_ROOT/usr/src/kernels/%{KVRFA}
    %{__ln_s} -f %{_usrsrc}/kernels/%{KVRFA} $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build
}

# Prepare the directories.
%{__rm} -rf $RPM_BUILD_ROOT
%{__mkdir_p} $RPM_BUILD_ROOT/boot
%{__mkdir_p} $RPM_BUILD_ROOT%{_libexecdir}

pushd linux-%{version}-%{release}.%{_target_cpu} > /dev/null

%if %{with_default}
BuildKernel
%endif

%if %{with_perf}
%global perf_make \
    %{__make} -s -C tools/perf %{?_smp_mflags} prefix=%{_prefix} lib=%{_lib} WERROR=0 HAVE_CPLUS_DEMANGLE=1 NO_GTK2=1 NO_LIBBABELTRACE=1 NO_LIBUNWIND=1 NO_LIBZSTD=1 NO_PERF_READ_VDSO32=1 NO_PERF_READ_VDSOX32=1 NO_STRLCPY=1

%{perf_make} all
%{perf_make} man
%endif

%if %{with_tools}
%ifarch x86_64
# Make sure that version-gen.sh is executable.
%{__chmod} +x tools/power/cpupower/utils/version-gen.sh
pushd tools/power/cpupower > /dev/null
%{__make} -s CPUFREQ_BENCH=false
popd > /dev/null
pushd tools/power/cpupower/debug/x86_64 > /dev/null
%{__make} -s centrino-decode
%{__make} -s powernow-k8-decode
popd > /dev/null
pushd tools/power/x86/x86_energy_perf_policy > /dev/null
%{__make} -s
popd > /dev/null
pushd tools/power/x86/turbostat > /dev/null
%{__make} -s
popd > /dev/null
%endif
pushd tools/thermal/tmon > /dev/null
%{__make} -s
popd > /dev/null
%endif

popd > /dev/null

%install
. /opt/rh/devtoolset-12/enable
export LLVM=1 LLVM_IAS=1 CC=clang

pushd linux-%{version}-%{release}.%{_target_cpu} > /dev/null

%if %{with_headers}
# We have to do the headers install before the tools install because the
# kernel headers_install will remove any header files in /usr/include that
# it doesn't install itself.

# Install kernel headers.
%{__make} -s ARCH=%{hdrarch} INSTALL_HDR_PATH=$RPM_BUILD_ROOT/usr headers_install

# Remove the unrequired files.
%{_bindir}/find $RPM_BUILD_ROOT/usr/include ! -name '*.h' -type f | \
    %{_bindir}/xargs --no-run-if-empty %{__rm} -f
%endif

%if %{with_doc}
DOCDIR=$RPM_BUILD_ROOT%{_datadir}/doc/%{name}-doc-%{version}

# Sometimes non-world-readable files sneak into the kernel source tree.
%{__chmod} -Rf a+rX,u+w,go-w Documentation

# Copy the documentation over.
%{__mkdir_p} $DOCDIR
%{__tar} -f - --exclude=man --exclude='.*' -c Documentation | %{__tar} -xf - -C $DOCDIR
%endif

%if %{with_perf}
# perf tool binary and supporting scripts/binaries.
%{perf_make} DESTDIR=$RPM_BUILD_ROOT install

# perf-python extension.
%{perf_make} DESTDIR=$RPM_BUILD_ROOT install-python_ext

# perf man pages. (Note: implicit rpm magic compresses them later.)
%{perf_make} DESTDIR=$RPM_BUILD_ROOT try-install-man
%endif

%if %{with_tools}
%ifarch x86_64
%{__make} -s -C tools/power/cpupower DESTDIR=$RPM_BUILD_ROOT libdir=%{_libdir} mandir=%{_mandir} CPUFREQ_BENCH=false install
%{__rm} -f %{buildroot}%{_libdir}/*.{a,la}
%find_lang cpupower
mv cpupower.lang ../
pushd tools/power/cpupower/debug/x86_64 > /dev/null
%{__install} -m755 centrino-decode %{buildroot}%{_bindir}/centrino-decode
%{__install} -m755 powernow-k8-decode %{buildroot}%{_bindir}/powernow-k8-decode
popd > /dev/null
%{__chmod} 0755 %{buildroot}%{_libdir}/libcpupower.so*
%{__mkdir_p} %{buildroot}%{_unitdir}
%{__install} -m644 %{SOURCE2} %{buildroot}%{_unitdir}/cpupower.service
%{__mkdir_p} %{buildroot}%{_sysconfdir}/sysconfig
%{__install} -m644 %{SOURCE3} %{buildroot}%{_sysconfdir}/sysconfig/cpupower
%{__mkdir_p} %{buildroot}%{_mandir}/man8
pushd tools/power/x86/x86_energy_perf_policy > /dev/null
%{__make} -s DESTDIR=%{buildroot} install
popd > /dev/null
pushd tools/power/x86/turbostat > /dev/null
%{__make} -s DESTDIR=%{buildroot} install
popd > /dev/null
%{_bindir}/find %{buildroot}%{_mandir} -type f -print0 | \
    %{_bindir}/xargs -0 --no-run-if-empty %{__chmod} 644
%endif
pushd tools/thermal/tmon > /dev/null
%{__install} -m755 tmon %{buildroot}%{_bindir}/tmon
popd > /dev/null
%endif

popd > /dev/null

%clean
%{__rm} -rf $RPM_BUILD_ROOT

# Scripts section.
%if %{with_default}
%triggerin -- microcode_ctl
KVERSION=%{version}-%{release}.%{_target_cpu}
if [ -e "/lib/modules/$KVERSION/modules.dep" ]; then
     %{_bindir}/dracut -f --kver $KVERSION
fi

%posttrans
%{_sbindir}/new-kernel-pkg --package %{name} --mkinitrd --dracut --depmod --update %{version}-%{release}.%{_target_cpu} || exit $?
%{_sbindir}/new-kernel-pkg --package %{name} --rpmposttrans %{version}-%{release}.%{_target_cpu} || exit $?
if [ -x %{_sbindir}/weak-modules ]; then
    %{_sbindir}/weak-modules --add-kernel %{version}-%{release}.%{_target_cpu} || exit $?
fi

%post
%{_sbindir}/new-kernel-pkg --package %{name} --install %{version}-%{release}.%{_target_cpu} || exit $?

%preun
%{_sbindir}/new-kernel-pkg --rminitrd --rmmoddep --remove %{version}-%{release}.%{_target_cpu} || exit $?
if [ -x %{_sbindir}/weak-modules ]; then
    %{_sbindir}/weak-modules --remove-kernel %{version}-%{release}.%{_target_cpu} || exit $?
fi

%postun
for i in `ls /boot/initramfs*kdump.img 2>/dev/null`; do
    KDVER=`echo $i | sed -e's/^.*initramfs-//' -e's/kdump.*$//'`
    if [ ! -e /boot/vmlinuz-$KDVER ]; then
        %{__rm} -f $i
    fi
done

%post devel
if [ -f /etc/sysconfig/kernel ]; then
    . /etc/sysconfig/kernel || exit $?
fi
if [ "$HARDLINK" != "no" -a -x %{_sbindir}/hardlink ]; then
    pushd %{_usrsrc}/kernels/%{version}-%{release}.%{_target_cpu} > /dev/null
    %{_bindir}/find . -type f | while read f; do
        %{_sbindir}/hardlink -c %{_usrsrc}/kernels/*.fc*.*/$f $f
    done
    popd > /dev/null
fi
%endif

%if %{with_tools}
%post -n %{name}-tools
%{_sbindir}/ldconfig || exit $?

%postun -n %{name}-tools
%{_sbindir}/ldconfig || exit $?
%endif

# Files section.
%if %{with_default}
%files
%defattr(-,root,root)
/boot/vmlinuz-%{version}-%{release}.%{_target_cpu}
%attr(600,root,root) /boot/System.map-%{version}-%{release}.%{_target_cpu}
/boot/symvers-%{version}-%{release}.%{_target_cpu}.gz
/boot/config-%{version}-%{release}.%{_target_cpu}
%dir /lib/modules/%{version}-%{release}.%{_target_cpu}
/lib/modules/%{version}-%{release}.%{_target_cpu}/kernel
/lib/modules/%{version}-%{release}.%{_target_cpu}/build
/lib/modules/%{version}-%{release}.%{_target_cpu}/source
/lib/modules/%{version}-%{release}.%{_target_cpu}/extra
/lib/modules/%{version}-%{release}.%{_target_cpu}/updates
/lib/modules/%{version}-%{release}.%{_target_cpu}/weak-updates
%ifarch %{vdso_arches}
/lib/modules/%{version}-%{release}.%{_target_cpu}/vdso
/etc/ld.so.conf.d/%{name}-%{version}-%{release}.%{_target_cpu}.conf
%endif
/lib/modules/%{version}-%{release}.%{_target_cpu}/modules.*
%ghost /boot/initramfs-%{version}-%{release}.%{_target_cpu}.img

%files devel
%defattr(-,root,root)
%dir %{_usrsrc}/kernels
%{_usrsrc}/kernels/%{version}-%{release}.%{_target_cpu}
%endif

%if %{with_headers}
%files headers
%defattr(-,root,root)
%{_includedir}/*
%endif

%if %{with_doc}
%files doc
%defattr(-,root,root)
%{_datadir}/doc/%{name}-doc-%{version}/Documentation/*
%dir %{_datadir}/doc/%{name}-doc-%{version}/Documentation
%dir %{_datadir}/doc/%{name}-doc-%{version}
%endif

%if %{with_perf}
%files -n perf
%defattr(-,root,root)
%{_bindir}/perf
%{_bindir}/trace
%{_libdir}/libperf-jvmti.so
#dir #{_includedir}/perf
#{_includedir}/perf/perf_dlfilter.h
%dir %{_usr}/lib/perf/examples/bpf
%{_usr}/lib/perf/examples/bpf/*
%dir %{_usr}/lib/perf/include/bpf
%{_usr}/lib/perf/include/bpf/*
%dir %{_libdir}/traceevent/plugins
%{_libdir}/traceevent/plugins/*
%dir %{_libexecdir}/perf-core
%{_libexecdir}/perf-core/*
%{_mandir}/man[1-8]/perf*
%config(noreplace) %{_sysconfdir}/bash_completion.d/perf
%dir %{_datadir}/perf-core/strace/groups
%{_datadir}/perf-core/strace/groups/*
%dir %{_datadir}/doc/perf-tip
%{_datadir}/doc/perf-tip/*
%doc linux-%{version}-%{release}.%{_target_cpu}/tools/perf/Documentation/examples.txt

%files -n python-perf
%defattr(-,root,root)
%{python_sitearch}
%endif

%if %{with_tools}
%files -n %{name}-tools -f cpupower.lang
%defattr(-,root,root)

%ifarch x86_64
%{_bindir}/cpupower
%{_bindir}/centrino-decode
%{_bindir}/powernow-k8-decode
%{_bindir}/x86_energy_perf_policy
%{_bindir}/turbostat
%{_bindir}/tmon
%config(noreplace) %{_sysconfdir}/sysconfig/cpupower
%{_unitdir}/cpupower.service
%{_prefix}/share/bash-completion/completions/cpupower
%{_mandir}/man[1-8]/cpupower*
%{_mandir}/man8/x86_energy_perf_policy*
%{_mandir}/man8/turbostat*

%files -n %{name}-tools-libs
%defattr(-,root,root)
%{_libdir}/libcpupower.so.1
%{_libdir}/libcpupower.so.0.0.1

%files -n %{name}-tools-libs-devel
%defattr(-,root,root)
%{_libdir}/libcpupower.so
%{_includedir}/cpufreq.h
%{_includedir}/cpuidle.h
%endif
%endif

%changelog
