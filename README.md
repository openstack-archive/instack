instack
=======

Execute diskimage-builder[1] elements on the current system.  This enables a
current running system to have an element applied in the same way that
diskimage-builder applies the element to an image build.

[1] https://github.com/stackforge/diskimage-builder

## Undercloud Install

1. Clone this repository

        git clone https://github.com/slagle/instack

2. Create and edit your answers file. The descriptions of the parameters that
   can be set are in the sample answers file.

        cd instack
        cp instack.answers.sample instack.answers
        # Return back to directory where instack was cloned
        cd ..

3. Run script to install undercloud. The script will produce a lot of output on
   the sceen. It also logs to ~/.instack/install-undercloud.log. You should see
   `install-undercloud Complete!` at the end of a successful run.

        instack/scripts/install-undercloud
