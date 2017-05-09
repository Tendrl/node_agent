NAME = python-etcd
VERSION = 0.4.3

all: srpm

clean:
	rm -rf dist/
	rm -rf $(NAME)-$(VERSION).tar.gz
	rm -rf $(NAME)-$(VERSION)-1.src.rpm

dist:
	git clone https://github.com/jplana/python-etcd python-etcd-0.4.3
	tar -zcvf python-etcd-0.4.3.tar.gz python-etcd-0.4.3
	rm -fr python-etcd-0.4.3

srpm: dist
	fedpkg --dist epel7 srpm

rpm:  srpm
	mock -r epel-7-x86_64 rebuild $(NAME)-$(VERSION)-1.src.rpm --resultdir=.

.PHONY: dist rpm srpm
