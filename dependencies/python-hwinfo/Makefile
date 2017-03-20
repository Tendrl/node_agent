NAME = python-hwinfo
VERSION = 0.1.6

all: srpm

clean:
	rm -rf dist/
	rm -rf $(NAME)-$(VERSION).tar.gz
	rm -rf $(NAME)-$(VERSION)-1.src.rpm
	rm -fr *.log

dist:
	git clone https://github.com/rdobson/python-hwinfo $(NAME)-$(VERSION)
	tar -zcvf $(NAME)-$(VERSION).tar.gz $(NAME)-$(VERSION)
	rm -fr $(NAME)-$(VERSION)

srpm: dist
	fedpkg --dist epel7 srpm
	fedpkg --dist epel6 srpm

rpm:  srpm
	mock -r epel-7-x86_64 rebuild $(NAME)-$(VERSION)-1.el7.src.rpm --resultdir=.
	mock -r epel-6-x86_64 rebuild $(NAME)-$(VERSION)-1.el6.src.rpm --resultdir=.

.PHONY: dist rpm srpm
