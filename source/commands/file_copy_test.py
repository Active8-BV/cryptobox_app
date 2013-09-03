# coding=utf-8
import os


def write_file(path, data, a_time, m_time, st_mode, st_uid, st_gid):
    """

    @param path:
    @param data:
    @param a_time:
    @param m_time:
    @param st_mode:
    @param st_uid:
    @param st_gid:
    """
    fout = open(path, "wb")
    fout.write(data)
    fout.close()
    os.utime(path, (a_time, m_time))
    os.chmod(path, st_mode)
    os.chown(path, st_uid, st_gid)


def read_file(path):
    """

    @param path:
    @return: @rtype:
    """
    data = open(path, "rb").read()
    stats = os.stat(path)
    return data, stats.st_atime, stats.st_mtime, stats.st_mode, stats.st_uid, stats.st_gid


def read_file_to_fdict(path):
    """

    @param path:
    @return: @rtype:
    """
    ft = read_file(path)
    file_dict = {"data": ft[0], "st_atime": int(ft[1]), "st_mtime": int(ft[2]), "st_mode": int(ft[3]), "st_uid": int(ft[4]), "st_gid": int(ft[5])}
    return file_dict


def write_fdict_to_file(fdict, path):
    """

    @param fdict:
    @param path:
    """
    write_file(path, fdict["data"], fdict["st_atime"], fdict["st_mtime"], fdict["st_mode"], fdict["st_uid"], fdict["st_gid"])


def main():
    """


    """
    fd = read_file_to_fdict("./gzip")
    write_fdict_to_file(fd, "./gzip_copy3")

    os.system("ls -las gzip*")


if __name__ == "__main__":
    main()
