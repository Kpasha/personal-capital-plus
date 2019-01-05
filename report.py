from requests import Session

from personalcapital.analyze import get_report


if __name__ == '__main__':
    report = get_report()
    session = Session()
    response = session.post("http://poorman.anthonyagnone.com/set_payload", json=report)
    print(response.status_code)
