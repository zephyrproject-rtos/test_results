
Test Result v2.4
################

Summary of testing activities and its results performed for the Zephyr RTOS.

Build tests
===========

This plan checks if all Zephyr tests and samples properly build on all platforms available in the release, that support corresponding features. Note that during this plan none of these tests is executed. More information about the plan can be found here [wiki  link]. Figure X.X shows a chart with the summary of this plan’s `results
<https://buildkite.com/zephyr/zephyr-daily>`_


On-target tests
===============

The on-target tests for a given version of Zephyr are executed by contributors on their sites. The status of all the tests executed for this release is found
`here
<https://testing.zephyrproject.org/daily_tests/index.html>`_ 
Summary of these tests results is given in Fig. X.X


Test coverage of new deliverables
=================================

`Table 1`_ shows a summarized scoring board for test coverage of new deliverables. A score for a given deliverable type is equal to the percentage of tested items of this type. A detailed table with an expanded explanation is given in the Appendix

`Table 1`_: Delivery Metrics scoring board
******************************************

.. _Table 1:

+--------------------+---------------+-----------------------+-----------+-----------+
| Summary            |    Verified   | Total                 | Failed    |  Score    |
+====================+===============+=======================+===========+===========+
|New platforms       | 2             | 20(boards)+ 3(shield) |    0      |  100*2/23 |
+--------------------+---------------+-----------------------+-----------+-----------+
|Platform removed    | -             | 1                     | -         | 100       |
+--------------------+---------------+-----------------------+-----------+-----------+
|Platform updated    | 1             | 1                     | 0         | 100       |
+--------------------+---------------+-----------------------+-----------+-----------+
|New API             | 0             | 0                     | 0         | 100       |
+--------------------+---------------+-----------------------+-----------+-----------+
|"API revision"_     | 1             | 1                     | 0         | 100       |
+--------------------+---------------+-----------------------+-----------+-----------+
|New FW/MW           | 1             | 1                     | 0         | 100       |
+--------------------+---------------+-----------------------+-----------+-----------+
|update FW/MW        | 2             | 2                     | 0         | 100       |
+--------------------+---------------+-----------------------+-----------+-----------+
|Tools               | 3             | 3                     | 0         | 100       |
+--------------------+---------------+-----------------------+-----------+-----------+
|Document            | 1             | 1                     | 0         | 100       |
+--------------------+---------------+-----------------------+-----------+-----------+

.. _API revision: https://docs.zephyrproject.org/latest/releases/release-notes-2.4.html#api-changes

Maintenance and performance metrics
===================================


Consistency metrics
*******************

`Table 2`_ lists all key features that we want to track, like a binary footprint, standard compatibility, etc., and test statuses of those. It serves to monitor consisten  cy between the releases.

`Table 2`_: Consistency Metrics
-------------------------------

.. _Table 2:

+---------------------+---------------------------------------------+-----------------------+
|Category             |     Name                                    | Steps                 |
+=====================+=============================================+=======================+
|Binary footprint     |app for commonly used kernel funcs footprint | `Binary footprint`_   |
+---------------------+---------------------------------------------+-----------------------+
| Standard compatible | -                                           |  Not Tested           |
+---------------------+---------------------------------------------+-----------------------+
|API compatible       | Not compatible with v2.3,                   |                       |
|                     | but keeps compatible with former posix      |  Not Tested           |
+---------------------+---------------------------------------------+-----------------------+


.. _Binary footprint: https://github.com/zephyrproject-rtos/zephyr/wiki/%5BHOW-TO%5D-Generate-a-binary-footprint-for-a-basic-Zephyr-application


Footprint metrics
*****************

A test from  Zephyr’s codebase called “footprints”  (footprints_)  is used to measure footprint results for the Zephyr application. Using this test application one can have the first impression about RAM and ROM usage, which will vary depending on the chosen platform (see Table 3). To know the detailed footprint for your board/platform/architecture run that test on your board (HOW TO). More details about the test are found in the Appendix. One can view the detailed test results by opening the “Detailed results link” in the RAM or ROM cell in `Table 3`_.

.. _footprints : https://github.com/zephyrproject-rtos/zephyr/tree/master/tests/benchmarks/footprints

`Table 3`_: Basic Zephyr application binary footprint
-----------------------------------------------------

.. _Table 3:

+---------------------+---------------+-----------------------+
|Board                |RAM (bytes)    |ROM (bytes)            |
+=====================+===============+=======================+
|reel_board           | 8335          | 29600                 |
+---------------------+---------------+-----------------------+
|up_squared           |12617296       | 4255088               |
+---------------------+---------------+-----------------------+
| iotdk               | 8017          | 17640                 |
+---------------------+---------------+-----------------------+
|frdm_k64f            |               |                       |
|(arm/cortex-m4)      | 8178          | 21888                 |
+---------------------+---------------+-----------------------+
|mimxrt685_evk_cm33   |               |                       |
|(arm/cortex-m33)     | 8111          | 27564                 |
+---------------------+---------------+-----------------------+
|mimxrt1064_evk       |               |                       |
|(arm/cortex-m7)      | 8746          | 29448                 |
+---------------------+---------------+-----------------------+

Security metrics
================

In this section, we summarized the test results of the security functionality and exception protection items defined by the Zephyr Security process (reference below) (see `Table 4`_). The aim of security metrics is to provide consistent insurance of security functionalities. A detailed description is given in the Reference Document.


`Table 4`_: Security Metrics Scoring Board
******************************************

.. _Table 4:

+-----------------------+----------+------+----------+
|Summary                |Verified  |Total |  Failed  |
+=======================+==========+======+==========+
|Security Functionality | 2        | 2    |  0       |
+-----------------------+----------+------+----------+
|Execution Protection   | 3        | 3    |  0       |
+-----------------------+----------+------+----------+


Static scan indexes
===================

`Security Link`_ summarizes the Coverity scan issues by providing a number of defects that remained open, grouped by severity level. This metric can help to estimate the code vulnerability.

.. _Security Link: https://docs.zephyrproject.org/latest/releases/release-notes-2.4.html#security-vulnerability-related

Defect metrics
==============

This chapter lists issues that are found by the release test(2020-09-06). The metrics are to provide the release defects index. 
We use the `defect filter`_ out issues found by test cases.


.. _defect filter: https://github.com/zephyrproject-rtos/zephyr/issues?q=is%3Aissue+label%3Abug+sort%3Aupdated-desc+label%3A%22area%3A+Tests%22+created%3A%3E2020-09-06 


`Table 6`_ is the scoring board for the metrics.

`Table 6`_: Release Defect Scoring Board
****************************************

.. _Table 6:

+-------------------------+---------------------------------+--------------------------+
|Index name               |  count                          | scores                   |
+=========================+=================================+==========================+
| Issue reported  per line|   0(high),8(medium), 15 (low)   | -1*(8*2+15) = -31        |
+-------------------------+---------------------------------+--------------------------+
| pass rate               |   -                             | 100                      |
+-------------------------+---------------------------------+--------------------------+
| remain issues           | -1*2(low)                       | -2                       |
+-------------------------+---------------------------------+--------------------------+

Note: the Scoring rules are
---------------------------

#.   -1 x count of founded issues during release test x severity(3: High, 2: medium, 1: low)

#.   Pass rate x 100

#.   -1 x Remianing issues x severity(3: High, 2: medium, 1: low)

Open Issues
===========

The release-readiness status is based on the number of open issues obtained with the community-defined filters being applied to the Zephyr RTOS GitHub repository. The current backlog of prioritized bugs was used as a quality metric to gate the final release. The limits are defined in the release process section of Zephyr documentation. `Table 7`_ shows the number of existing issues with the above filters applied and the allowed limits for each priority.

`Table 7`_: Number of currently open issues (with filters applied) and limits for each priority level
*****************************************************************************************************

.. _Table 7:

+-------------------------+---------------------+--------------------------+
|Priority                 | Current             |    Max allowed           |
+=========================+=====================+==========================+
|High                     | 1                   |   0                      |
+-------------------------+---------------------+--------------------------+
| Medium                  | 20                  |   20                     |
+-------------------------+---------------------+--------------------------+
| Low                     | 142                 | 150                      |
+-------------------------+---------------------+--------------------------+

The numbers of new issues found: highlight or list the most significant issues, especially if any issues are considered blocking issues. High-level comments, including a discussion of blocking issues, testing gaps, and recommendations. Only labeled for the current release.


*Add table to track Coverage of the requirements. HTML page which is generated by Sanitycheck coverage option.*

**TBD**



