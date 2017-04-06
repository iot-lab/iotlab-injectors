from runner import run


def test_datasets_no_args():
    run("datasets")


def test_datasets_list():
    ret = run("datasets --list")

    assert "synthetic" in ret
    assert "citypulse" in ret


def test_citypulse_traffic_download():
    run("datasets --download --dataset citypulse --event traffic")

    import os
    assert os.path.isdir("embers.datasets.citypulse")

    import embers.datasets.citypulse.traffic as traffic
    t = traffic.Traffic()
    s = t.get_source(0)
    d = s.next()

    assert "vehicleCount" in d
    assert "avgSpeed" in d
