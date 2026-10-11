from types import SimpleNamespace

import pytest

from jev_ultrafast.browser import StalePage
from scripts.paired_browser_server import execute_direct


@pytest.mark.parametrize('error,expected', [(StalePage('changed before input'), 'not_executed'),
                                           (RuntimeError('connection lost after dispatch'), 'uncertain')])
def test_direct_rejection_does_not_hide_uncertain_execution(error, expected):
    events, mutations = [], []

    def act(*args, **kwargs):
        raise error

    journal = SimpleNamespace(write=lambda event, **details: events.append((event, details)))
    browser = SimpleNamespace(act=act)
    if expected == 'not_executed':
        result = execute_direct(browser, {}, {'label': 'Observed field'}, 'Supplied text', mutations, journal)
        assert result == {'execution': 'not_executed', 'observe_again': True}
        assert mutations == []
        assert events[-1][0] == 'rejected'
    else:
        with pytest.raises(RuntimeError):
            execute_direct(browser, {}, {'label': 'Observed field'}, 'Supplied text', mutations, journal)
        assert len(mutations) == 1
        assert mutations[0]['execution'] == 'uncertain'
        assert events[-1][0] == 'mutation_started'
