"""Realiza importaciones de módulos.

Realiza importaciones de módulos o paquetes git en
forma de árbol para desarrollo en pip

"""
import os
import re


def __importar_deps(deps_importadas: list[str],
                    rut_arch: str) -> list[str]:
    """Método privado, importa las dependencias.

    Parameters
    ----------
    deps_importadas
        Dependencias importadas
    rut_arch
        Ruta del archivo

    Returns
    -------
    list[str]
        Dependencias importadas
    """
    # Obtiene las dependencias a importar
    with open(rut_arch, 'r', encoding='utf8') as arch:

        texto = arch.read()
        if "setup.py" in rut_arch:
            lista = re.findall("install_requires=\\[[\\s\\S]+\\]", texto)
            if lista:
                texto = re.sub("[\\s]",
                               "",
                               lista[0])
                texto = re.sub("\'.+\\@(.+)\\+url_release\\(\".+\"\\)",
                               "\'\\g<1>",
                               texto)
                texto = re.sub("install_requires=\\[(.+)\\]",
                               "\\g<1>",
                               texto)
                texto = re.sub("\'",
                               "",
                               texto)
                lista = texto.split(",")
        else:
            texto = re.sub("[\\s]",
                           ",",
                           texto)
            texto = re.sub("/releases+[/\\w\\.]+",
                           "",
                           texto)
            lista = texto.split(",")

        deps_importar = [val
                        for val in lista
                        if val not in deps_importadas]

    # Importa las dependencias sean de git o no
    for dep_importar in deps_importar:
        if dep_importar not in deps_importadas:
            if "http" in dep_importar:
                nombre_rep_dep = dep_importar.split('/').pop()
                rut_arch = nombre_rep_dep + '\\setup.py'
                os.system('git clone ' + dep_importar)
                os.system('pip install --no-deps -e ' + nombre_rep_dep)
                deps_importadas += [dep_importar]
                if os.path.isfile(rut_arch):
                    deps_importadas = __importar_deps(
                        deps_importadas,
                        rut_arch)
            else:
                os.system('pip install ' + dep_importar)
                deps_importadas += [dep_importar]

    return deps_importadas


def importar_repositorio(url_rep: str) -> None:
    """Hace la importación del módulo git principal.

    Parameters
    ----------
    url_rep
        URL del repositorio
    """
    nombre_rep = url_rep.split('/').pop()

    # Importa el repositorio correspondiente
    if not os.path.isdir(nombre_rep):

        os.system('git clone ' + url_rep)

        # Importa las dependencias de git
        rut_arch = ""
        if os.path.isfile(nombre_rep + '/setup.py'):
            rut_arch = nombre_rep + "/setup.py"
        if os.path.isfile(nombre_rep + '/requirements.txt'):
            rut_arch = nombre_rep + "/requirements.txt"

        __importar_deps([], rut_arch)
