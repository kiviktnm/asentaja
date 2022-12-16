import arconf
import arconf.system

class Nvidia:
    # Note that currently configuring nvidia settings in arconf is not supported
    enable = False

    package = "nvidia"
    utils_package = "nvidia-utils"

    enable32bit = False
    package32bit = "lib32-nvidia-utils"

    prime_offload = False
    # This has been directly copied from the Arch Linux Wiki (https://wiki.archlinux.org/title/PRIME#NVIDIA)
    prime_offload_udev_rules = '''# Enable runtime PM for NVIDIA VGA/3D controller devices on driver bind
ACTION=="bind", SUBSYSTEM=="pci", ATTR{vendor}=="0x10de", ATTR{class}=="0x030000", TEST=="power/control", ATTR{power/control}="auto"
ACTION=="bind", SUBSYSTEM=="pci", ATTR{vendor}=="0x10de", ATTR{class}=="0x030200", TEST=="power/control", ATTR{power/control}="auto"

# Disable runtime PM for NVIDIA VGA/3D controller devices on driver unbind
ACTION=="unbind", SUBSYSTEM=="pci", ATTR{vendor}=="0x10de", ATTR{class}=="0x030000", TEST=="power/control", ATTR{power/control}="on"
ACTION=="unbind", SUBSYSTEM=="pci", ATTR{vendor}=="0x10de", ATTR{class}=="0x030200", TEST=="power/control", ATTR{power/control}="on"'''
    prime_offload_module_params = '''options nvidia "NVreg_DynamicPowerManagement=0x02"'''

    def apply(self):
        if self.enable:
            arconf.packages += [ self.package, self.utils_package ]

            # No need to add a pacman hook since arconf automatically updates initramfs every time anyways

            arconf.system.boot.kernel_parameters += [ "nvidia_drm.modeset=1" ]
            arconf.system.boot.mkinitcpio_modules += [ "nvidia", "nvidia_modeset", "nvidia_uvm", "nvidia_drm" ]

            if self.enable32bit:
                arconf.packages += [ self.package32bit ]

            if self.prime_offload:
                arconf.packages += [ "nvidia-prime" ]
                arconf.file_mappings["/etc/udev/rules.d/80-nvidia-pm.rules"] = arconf.FileMapping(content=self.prime_offload_udev_rules)
                arconf.file_mappings["/etc/modprobe.d/nvidia-pm.conf"] = arconf.FileMapping(content=self.prime_offload_module_params)
                arconf.enabled_services += [ "nvidia-persistenced.service" ]


