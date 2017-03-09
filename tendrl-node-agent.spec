%define use_systemd (0%{?fedora} && 0%{?fedora} >= 18) || (0%{?rhel} && 0%{?rhel} >= 7)
Name: tendrl-node-agent
Version: 1.2.1
Release: 1%{?dist}
BuildArch: noarch
Summary: Module for Tendrl Node Agent
Source0: %{name}-%{version}.tar.gz
License: LGPLv2+
URL: https://github.com/Tendrl/node-agent

BuildRequires: ansible
BuildRequires: python-gevent
BuildRequires: python-etcd
BuildRequires: python-urllib3
BuildRequires: python2-devel
BuildRequires: pytest
%if %{use_systemd}
BuildRequires: systemd
%endif
BuildRequires: python-mock

Requires: ansible
Requires: python-etcd
Requires: python-gevent
Requires: python-greenlet
Requires: collectd
Requires: python-jinja2
Requires: tendrl-commons
Requires: python-hwinfo 
Requires: python-netifaces
Requires: python-netaddr

%description
Python module for Tendrl node bridge to manage storage node in the sds cluster

%prep
%setup

# Remove bundled egg-info
rm -rf %{name}.egg-info

%build
%{__python} setup.py build

# remove the sphinx-build leftovers
rm -rf html/.{doctrees,buildinfo}

%install
%{__python} setup.py install --single-version-externally-managed -O1 --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES
install -m  0755  --directory $RPM_BUILD_ROOT%{_var}/log/tendrl/node-agent
install -m  0755  --directory $RPM_BUILD_ROOT%{_sysconfdir}/tendrl/node-agent
install -m  0755  --directory $RPM_BUILD_ROOT%{_datadir}/tendrl/node-agent
install -m  0755  --directory $RPM_BUILD_ROOT%{_sharedstatedir}/tendrl
%if %{use_systemd}
install -Dm 0644 tendrl-node-agent.service $RPM_BUILD_ROOT%{_unitdir}/tendrl-node-agent.service
install -Dm 0644 tendrl-message.socket $RPM_BUILD_ROOT%{_unitdir}/tendrl-message.socket
%else
install -D -m 755 node-agent.el6.service %{buildroot}%{_initrddir}/node-agent
%endif
install -Dm 0644 etc/tendrl/node-agent/node-agent.conf.yaml.sample $RPM_BUILD_ROOT%{_sysconfdir}/tendrl/node-agent/node-agent.conf.yaml
install -Dm 0644 etc/tendrl/node-agent/logging.yaml.syslog.sample $RPM_BUILD_ROOT%{_sysconfdir}/tendrl/node-agent/node-agent_logging.yaml
install -Dm 644 etc/tendrl/node-agent/*.sample $RPM_BUILD_ROOT%{_datadir}/tendrl/node-agent/

%post
getent group tendrl >/dev/null || groupadd -r tendrl
%if %use_systemd
%systemd_post tendrl-node-agent.service
%else
/sbin/chkconfig --add node-agent
%endif

%preun
%if %use_systemd
%systemd_preun tendrl-node-agent.service
%else
/sbin/service node-agent stop > /dev/null 2>&1
/sbin/chkconfig --del node-agent
%endif

%postun
%if %use_systemd
%systemd_postun_with_restart tendrl-node-agent.service
%endif

%check
py.test -v tendrl/node-agent/tests || :

%files -f INSTALLED_FILES
%dir %{_var}/log/tendrl/node-agent
%dir %{_sysconfdir}/tendrl/node-agent
%dir %{_datadir}/tendrl/node-agent
%dir %{_sharedstatedir}/tendrl
%doc README.rst
%license LICENSE
%{_datadir}/tendrl/node-agent/
%{_sysconfdir}/tendrl/node-agent/node-agent.conf.yaml
%{_sysconfdir}/tendrl/node-agent/node-agent_logging.yaml
%if %{use_systemd}
%{_unitdir}/tendrl-node-agent.service
%{_unitdir}/tendrl-message.socket
%else
%{_initrddir}/node-agent
%endif

%changelog
* Tue Nov 01 2016 Timothy Asir Jeyasingh <tjeyasin@redhat.com> - 0.0.1-1
- Initial build.
