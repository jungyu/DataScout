import pkg_resources
import subprocess

# 獲取已安裝的套件
installed_packages = [pkg.key for pkg in pkg_resources.working_set]

# 排除基礎套件
exclude_packages = {'pip', 'setuptools', 'wheel'}
packages_to_remove = [pkg for pkg in installed_packages if pkg not in exclude_packages]

# 卸載套件
for package in packages_to_remove:
    try:
        subprocess.check_call(['pip', 'uninstall', '-y', package])
    except subprocess.CalledProcessError:
        print(f"無法卸載 {package}")