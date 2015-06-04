To do a new build of instack you need to:

1. Go to your git checkout of instack
1. Commit any updates, then make an annotated tag, if the previous version was
   0.0.2, the new tag would be called 0.0.3.

        git tag -a 0.0.3

1. Push any changes and the tag.

        git push --tags

1. Build an sdist tarball for the release. This command would create
   instack-0.0.3.tar.gz under the dist directory.

        python setup.py sdist

1. Go to github for instack, https://github.com/rdo-management/instack/releases/

1. Click Draft a new release

1. Enter the tag you've created, github should tell you it's an existing tag

1. Upload the tgz created earlier to the release.

1. Update the specfile Version in dist-git and rebuild.
