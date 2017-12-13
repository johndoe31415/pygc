# pygc
pygc (pronounced "Pixie") stands for "Python Glass Cockpit" and is some
software in very early development (read: "unusable") that aims to provide a
Garmin-like glass cockpit for aviation simulation. I.e., a glass-cockpit that
can run off a Raspberry Pi on a separate monitor and that receives flight
parameters (yaw, pitch, roll, GPS position, AP state, CRS/HDG, IAS, etc) from
the running simulation via network and renders them nicely.

Nothing of this works, yet. It's just some attempts with libcairo and inkscape
so far, don't get your hopes up, sorry. It's just some attempts to get this all
working in a manner that actually performs well enough to be smooth (i.e.,
target is 60fps) on a Pi3.

# License
Everything is licensed under the GNU GPL-3.
