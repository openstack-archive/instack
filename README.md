Team and repository tags
========================

[![Team and repository tags](https://governance.openstack.org/tc/badges/instack.svg)](https://governance.openstack.org/tc/reference/tags/index.html)

<!-- Change things from this point on -->

instack
=======

instack executes [diskimage-builder](https://github.com/openstack/diskimage-builder)
style elements on the current system.  This enables a
current running system to have an element applied in the same way that
diskimage-builder applies the element to an image build.

instack, in its current form, should be considered low level tooling. It is meant
to be used by higher level scripting that understands what elements and
hook scripts need execution. Using instack requires a rather in depth
knowledge of the elements within diskimage-builder and tripleo-image-elements.

An example of higher level tooling that uses instack to install a TripleO style
undercloud is at:
https://github.com/rdo-management/instack-undercloud
