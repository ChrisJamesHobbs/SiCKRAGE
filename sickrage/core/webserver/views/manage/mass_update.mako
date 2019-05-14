<%inherit file="../layouts/main.mako"/>
<%!
    from functools import cmp_to_key

    import sickrage
    from sickrage.core.tv.show.helpers import get_show_list
    from sickrage.core.common import SKIPPED, WANTED, UNAIRED, ARCHIVED, IGNORED, SNATCHED, SNATCHED_PROPER, SNATCHED_BEST, FAILED
    from sickrage.core.common import statusStrings
    from sickrage.core.helpers.compat import cmp
%>

<%block name="sub_navbar">
    <div class="row submenu">
        <div class="col">
            <button class="btn" id="submitMassEdit">${_('Mass Edit')}</button>
            <button class="btn" id="submitMassUpdate">${_('Mass Update')}</button>
            <button class="btn" id="submitMassRescan">${_('Mass Rescan')}</button>
            <button class="btn" id="submitMassRename">${_('Mass Rename')}</button>
            <button class="btn" id="submitMassDelete">${_('Mass Delete')}</button>
            <button class="btn" id="submitMassRemove">${_('Mass Remove')}</button>
            % if sickrage.app.config.use_subtitles:
                <button class="btn" id="submitMassSubtitle">${_('Mass Subtitle')}</button>
            % endif
        </div>
        <div class="col text-right">
            <div class="dropdown ml-4" id="checkboxControls">
                <button type="button" class="btn bg-transparent dropdown-toggle" data-toggle="dropdown"
                        style="border: none;">
                    <i class="fas fa-2x fa-columns"></i>
                </button>
                <div class="dropdown-menu dropdown-menu-right">
                    <a class="dropdown-item" href="#">
                        <label>
                            <input type="checkbox" id="Continuing" checked="checked"/>
                            ${_('Continuing')}
                        </label>
                    </a>
                    <a class="dropdown-item" href="#">
                        <label>
                            <input type="checkbox" id="Ended" checked="checked"/>
                            ${_('Ended')}
                        </label>
                    </a>
                </div>
            </div>
        </div>
    </div>
</%block>

<%block name="content">
    <%namespace file="../includes/quality_defaults.mako" import="renderQualityPill"/>

    <div class="row">
        <div class="col-lg-10 mx-auto">
            <div class="card mb-3">
                <div class="card-header">
                    <h3>${title}</h3>
                </div>
                <div class="card-body">
                    <div class="table-responsive">
                        <table id="massUpdateTable" class="table">
                            <thead class="thead-dark">
                            <tr>
                                <th class="col-checkbox">
                                    <input type="checkbox" class="bulkCheck" id="checkAll"/>
                                </th>
                                <th>${_('Show Name')}</th>
                                <th>${_('Show Directory')}</th>
                                <th class="col-quality">${_('Quality')}</th>
                                <th class="col-legend">${_('Sports')}</th>
                                <th class="col-legend">${_('Scene')}</th>
                                <th class="col-legend">${_('Anime')}</th>
                                <th class="col-legend">${_('Season folders')}</th>
                                <th class="col-legend">${_('Skip downloaded')}</th>
                                <th class="col-legend">${_('Paused')}</th>
                                <th class="col-legend">${_('Subtitle')}</th>
                                <th class="col-legend">${_('Default Ep Status')}</th>
                                <th class="col-legend">${_('Status')}</th>
                            </tr>
                            </thead>

                            <tbody>
                                % for curShow in sorted(get_show_list(), key=cmp_to_key(lambda x, y: x.name < y.name)):
                                    <% curEp = curShow.airs_next %>

                                    <tr class="${curShow.status}" id="${curShow.indexer_id}">
                                        <td class="table-fit">
                                            <input type="checkbox" class="showCheck" id="${curShow.indexer_id}"
                                                   name="${curShow.indexer_id}" ${('disabled', '')[bool(not any([
                                            sickrage.app.show_queue.is_being_renamed(curShow.indexer_id),
                                            sickrage.app.show_queue.is_in_rename_queue(curShow.indexer_id),
                                            sickrage.app.show_queue.is_in_refresh_queue(curShow.indexer_id),
                                            sickrage.app.show_queue.is_being_updated(curShow.indexer_id),
                                            sickrage.app.show_queue.is_in_update_queue(curShow.indexer_id),
                                            sickrage.app.show_queue.is_being_refreshed(curShow.indexer_id),
                                            sickrage.app.show_queue.is_in_refresh_queue(curShow.indexer_id),
                                            sickrage.app.show_queue.is_being_renamed(curShow.indexer_id),
                                            sickrage.app.show_queue.is_in_rename_queue(curShow.indexer_id),
                                            sickrage.app.show_queue.is_being_subtitled(curShow.indexer_id),
                                            sickrage.app.show_queue.is_in_subtitle_queue(curShow.indexer_id)]))]}/>
                                        </td>
                                        <td class="tvShow">
                                            <a href="${srWebRoot}/home/displayShow?show=${curShow.indexer_id}">${curShow.name}</a>
                                        </td>
                                        <td>
                                            ${curShow.location}
                                        </td>
                                        <td class="table-fit">${renderQualityPill(curShow.quality, showTitle=True)}</td>
                                        <td class="table-fit">
                                            <i class="fa ${("fa-times text-danger", "fa-check text-success")[bool(curShow.is_sports)]}"></i>
                                            <span class="d-none d-print-inline">${bool(curShow.is_sports)}</span>
                                        </td>
                                        <td class="table-fit">
                                            <i class="fa ${("fa-times text-danger", "fa-check text-success")[bool(curShow.is_scene)]}"></i>
                                            <span class="d-none d-print-inline">${bool(curShow.is_scene)}</span>
                                        </td>
                                        <td class="table-fit">
                                            <i class="fa ${("fa-times text-danger", "fa-check text-success")[bool(curShow.is_anime)]}"></i>
                                            <span class="d-none d-print-inline">${bool(curShow.is_anime)}</span>
                                        </td>
                                        <td class="table-fit">
                                            <i class="fa ${("fa-times text-danger", "fa-check text-success")[not bool(curShow.flatten_folders)]}"></i>
                                            <span class="d-none d-print-inline">${bool(curShow.flatten_folders)}</span>
                                        </td>
                                        <td class="table-fit">
                                            <i class="fa ${("fa-times text-danger", "fa-check text-success")[bool(curShow.skip_downloaded)]}"></i>
                                            <span class="d-none d-print-inline">${bool(curShow.skip_downloaded)}</span>
                                        </td>
                                        <td class="table-fit">
                                            <i class="fa ${("fa-times text-danger", "fa-check text-success")[bool(curShow.paused)]}"></i>
                                            <span class="d-none d-print-inline">${bool(curShow.paused)}</span>
                                        </td>
                                        <td class="table-fit">
                                            <i class="fa ${("fa-times text-danger", "fa-check text-success")[bool(curShow.subtitles)]}"></i>
                                            <span class="d-none d-print-inline">${bool(curShow.subtitles)}</span>
                                        </td>
                                        <td class="table-fit">
                                            ${statusStrings[curShow.default_ep_status]}
                                        </td>
                                        <td class="table-fit">
                                            ${curShow.status}
                                        </td>
                                    </tr>
                                % endfor
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>
</%block>
