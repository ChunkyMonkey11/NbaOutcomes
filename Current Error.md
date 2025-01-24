C:\Users\Revant\NbaOutcomes\mywebsite> python manage.py update_predictions
Fetching NBA predictions...
Traceback (most recent call last):
  File "C:\Users\Revant\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.9_qbz5n2kfra8p0\LocalCache\local-packages\Python39\site-packages\pandas\core\indexes\base.py", line 3805, in get_loc
    return self._engine.get_loc(casted_key)
  File "index.pyx", line 167, in pandas._libs.index.IndexEngine.get_loc
  File "index.pyx", line 196, in pandas._libs.index.IndexEngine.get_loc
  File "pandas\\_libs\\hashtable_class_helper.pxi", line 7081, in pandas._libs.hashtable.PyObjectHashTable.get_item
  File "pandas\\_libs\\hashtable_class_helper.pxi", line 7089, in pandas._libs.hashtable.PyObjectHashTable.get_item
KeyError: 'AVG_TOTAL_home_away_adjusted'

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "C:\Users\Revant\NbaOutcomes\mywebsite\manage.py", line 22, in <module>
    main()
  File "C:\Users\Revant\NbaOutcomes\mywebsite\manage.py", line 18, in main
    execute_from_command_line(sys.argv)
  File "C:\Users\Revant\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.9_qbz5n2kfra8p0\LocalCache\local-packages\Python39\site-packages\django\core\management\__init__.py", line 442, in execute_from_command_line
    utility.execute()
  File "C:\Users\Revant\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.9_qbz5n2kfra8p0\LocalCache\local-packages\Python39\site-packages\django\core\management\__init__.py", line 436, in execute
    self.fetch_command(subcommand).run_from_argv(self.argv)
  File "C:\Users\Revant\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.9_qbz5n2kfra8p0\LocalCache\local-packages\Python39\site-packages\django\core\management\base.py", line 412, in run_from_argv
    self.execute(*args, **cmd_options)
  File "C:\Users\Revant\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.9_qbz5n2kfra8p0\LocalCache\local-packages\Python39\site-packages\django\core\management\base.py", line 458, in execute
    output = self.handle(*args, **options)
  File "C:\Users\Revant\NbaOutcomes\mywebsite\peltzerspicks\management\commands\update_predictions.py", line 216, in handle
    PREDICTIONS = make_predictions()
  File "C:\Users\Revant\NbaOutcomes\mywebsite\peltzerspicks\management\commands\update_predictions.py", line 198, in make_predictions
    df['predicted_total_home_away_adjusted'] = .5*(df['AVG_TOTAL_home_away_adjusted']+df['AVG_TOTAL_home_away_adjusted_opp'])
  File "C:\Users\Revant\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.9_qbz5n2kfra8p0\LocalCache\local-packages\Python39\site-packages\pandas\core\frame.py", line 4102, in __getitem__
    indexer = self.columns.get_loc(key)
  File "C:\Users\Revant\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.9_qbz5n2kfra8p0\LocalCache\local-packages\Python39\site-packages\pandas\core\indexes\base.py", line 3812, in get_loc
    raise KeyError(key) from err
KeyError: 'AVG_TOTAL_home_away_adjusted'
