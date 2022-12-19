import psycopg2
from collections import namedtuple
import uuid



class Db:

    conn = None

    def connect(self) -> any:
        connection = psycopg2.connect(
            host="192.168.86.27",
            database="arb",
            user="uzer",
            password="Fantazi669")

        # create a cursor
        cur = connection.cursor()

        # execute a statement
        print('PostgreSQL database version:')
        cur.execute('SELECT version()')
        print('Connected to DB.')

        # display the PostgreSQL database server version
        db_version = cur.fetchone()
        print(db_version)
        return connection

    def get_run_id(self, strategy, exchange_name):
        try:
            cur = self.conn.cursor()
            sql = "SELECT strategy_name, exchange, run_id, total_phases, last_phase_completed, last_change_date, create_date " + \
            "FROM strategies where last_phase_completed != total_phases and strategy_name = %s and exchange = %s"
            cur.execute(sql, (str(strategy), str(exchange_name)))
            strategy = cur.fetchone()
            #print(strategy)
            if strategy is None:
                return None, None
            else:
                return strategy[2], strategy[4]
        except Exception as e:
            print(e)
            return None

    def insert_strategy(self, strategy, exchange_name, run_id, total_phases):
        try:
            cur = self.conn.cursor()

            sql = "insert into strategies(strategy_name, exchange, run_id, total_phases, last_phase_completed) values(%s, %s, %s, %s, %s)"
            cur.execute(sql, (strategy, exchange_name, str(run_id), str(total_phases), 0))
            self.conn.commit()

            cur.close()
            print("Strategy inserted: " + strategy + ", " + exchange_name + ", " + str(run_id) + " Logged.")
        except Exception as e:
            print(e)

    def insert_strategy_log_entry(self, strategy, exchange_name, action, action_id, output, run_id):
        try:
            cur = self.conn.cursor()

            sql = "insert into strategies_log(name, action, action_id, exchange_name, output, run_id) values(%s, %s, %s, %s, %s, %s)"
            cur.execute(sql, (strategy, action, str(action_id), str(exchange_name), str(output), str(run_id)))
            self.conn.commit()

            cur.close()
            print("Strategy Action: " + strategy + ", " + exchange_name + ", " + str(run_id) + ", " + action + " Logged.")
        except Exception as e:
            print(e)

    def start_strategy(self, strategy, exchange_name, total_phases):
        # see if we continue existing run or start new run
        (run_id, last_phase_completed) = self.get_run_id(strategy, exchange_name)

        if run_id is None:
            #start new run
            run_id = uuid.uuid1()
            last_phase_completed = 0

            self.insert_strategy(strategy, exchange_name, run_id, total_phases)
            self.insert_strategy_log_entry(strategy, exchange_name, "STARTING STRATEGY", None, None, run_id)
        else:
            #continue existing run
            self.insert_strategy_log_entry(strategy, exchange_name, "CONTINUING STRATEGY", None, None, run_id)

        return run_id, last_phase_completed

    def end_strategy(self, strategy, exchange_name, run_id):
        self.insert_strategy_log_entry(strategy, exchange_name, "ENDING STRATEGY", None, None, run_id)

    def init(self, strategy, exchange_name, total_phases) -> any:
        self.conn = self.connect()
        run_id, last_phase_completed = self.start_strategy(strategy, exchange_name, total_phases)
        return run_id, last_phase_completed

    def close(self, strategy, exchange_name, run_id) -> bool:
        self.end_strategy(strategy, exchange_name, run_id)
        self.conn.close()
        return True

    def log_action(self, strategy, exchange_name, action, action_id, output, run_id) -> bool:
        self.insert_strategy_log_entry(strategy, exchange_name, action, action_id, output, run_id)

    def set_next_phase(self, run_id) -> int:
        try:
            cur = self.conn.cursor()

            sql = "update strategies set last_phase_completed = last_phase_completed + 1 where run_id = '" + str(run_id) + "'"
            cur.execute(sql)
            self.conn.commit()

            cur.close()
            print("Next phase set")
        except Exception as e:
            print(e)

        return self.get_current_phase(run_id)

    def get_current_phase(self, run_id) -> int:
        try:
            cur = self.conn.cursor()

            sql = "select last_phase_completed from strategies where run_id = '" + str(run_id) + "'"
            cur.execute(sql)
            result = cur.fetchone()
            if result is None:
                return None
            else:
                return int(result[0])
        except Exception as e:
            print(e)
            return None

    def get_action_id(self, run_id) -> str:
        try:
            cur = self.conn.cursor()

            sql = "select action_id from strategies_log where action = %s and run_id = %s order by id desc"
            cur.execute(sql, ('ORDER PLACED', str(run_id)))
            result = cur.fetchone()
            if result is None:
                return None
            else:
                return str(result[0])
        except Exception as e:
            print(e)
            return None

    def set_specific_phase(self, run_id, phase) -> int:
        try:
            cur = self.conn.cursor()

            sql = "update strategies set last_phase_completed = %s where run_id = '" + str(run_id) + "'"
            cur.execute(sql, (phase, ))
            self.conn.commit()

            cur.close()
            print("Next phase set")
        except Exception as e:
            print(e)





