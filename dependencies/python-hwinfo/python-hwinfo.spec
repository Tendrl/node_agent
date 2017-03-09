%define name python-hwinfo
%define version 0.1.6
%define unmangled_version 0.1.6
%define unmangled_version 0.1.6
%define release 1

Summary: Library for parsing hardware info on Linux OSes.
Name: %{name}
Version: %{version}
Release: %{release}
Source0: %{name}-%{unmangled_version}.tar.gz
License: GPLV2.1
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildArch: noarch
Vendor: Rob Dobson <rob@rdobson.co.uk>
Url: https://github.com/rdobson/python-hwinfo

BuildRequires: python-setuptools

%description
python-hwinfo documentation
This is a python library for inspecting hardware and devices by
parsing the outputs of system utilities such as lspci and dmidecode.

%prep
%setup -n %{name}-%{unmangled_version} -n %{name}-%{unmangled_version}

%build
python setup.py build

%install
python setup.py install --single-version-externally-managed -O1 --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES

%clean
rm -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES
%defattr(-,root,root)
