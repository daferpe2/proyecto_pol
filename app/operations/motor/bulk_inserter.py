class BulkInserter:
    def insert(self, models: list, session):
        if not models:
            return 0

        try:
            # PostgreSQL: bulk real
            try:
                session.bulk_save_objects(models)
                session.commit()
                return len(models)

            except Exception:
                # SQLite fallback
                session.rollback()
                for m in models:
                    session.add(m)
                session.commit()
                return len(models)

        except Exception as e:
            session.rollback()
            raise Exception(f"DatabaseError: {str(e)}")
