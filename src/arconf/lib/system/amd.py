import arconf
import arconf.system

class AMD:
    enable = False
    ati = False

    enable32bit = False

    def apply(self):
        if self.enable:
            arconf.packages += [
                "mesa",
                "libva-mesa-driver",
                "mesa-vdpau"
            ]

            if self.ati:
                arconf.packages += [ "xf86-video-ati" ]
                arconf.system.boot.mkinitcpio_modules += [ "radeon" ]
            else:
                arconf.system.boot.mkinitcpio_modules += [ "amdgpu" ]
                arconf.packages += [ "xf86-video-amdgpu", "vulkan-radeon" ]
                if self.enable32bit:
                    arconf.packages += [ "lib32-vulkan-radeon" ]

            if self.enable32bit:
                arconf.packages += [
                    "lib32-mesa",
                    "lib32-libva-mesa-driver",
                    "lib32-mesa-vdpau"
                ]

