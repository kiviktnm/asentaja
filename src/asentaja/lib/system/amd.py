import asentaja
import asentaja.system

class AMD:
    enable = False
    ati = False

    enable32bit = False

    def apply(self):
        if self.enable:
            asentaja.packages += [
                "mesa",
                "libva-mesa-driver",
                "mesa-vdpau"
            ]

            if self.ati:
                asentaja.packages += [ "xf86-video-ati" ]
                asentaja.system.boot.mkinitcpio_modules += [ "radeon" ]
            else:
                asentaja.system.boot.mkinitcpio_modules += [ "amdgpu" ]
                asentaja.packages += [ "xf86-video-amdgpu", "vulkan-radeon" ]
                if self.enable32bit:
                    asentaja.packages += [ "lib32-vulkan-radeon" ]

            if self.enable32bit:
                asentaja.packages += [
                    "lib32-mesa",
                    "lib32-libva-mesa-driver",
                    "lib32-mesa-vdpau"
                ]

