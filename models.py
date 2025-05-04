from typing import Optional, List

from sqlmodel import SQLModel, Field, Relationship, select

from db import SessionDep


class SynonymModel(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    word: str = Field(index=True, unique=True)
    synonym: Optional[str] = Field(default=None)


class SynonymLink(SQLModel, table=True):
    word_id: Optional[int] = Field(default=None, foreign_key="word.id", primary_key=True)
    synonym_id: Optional[int] = Field(default=None, foreign_key="word.id", primary_key=True)


class Word(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    word: str = Field(index=True, unique=True)

    # Direct synonyms
    synonyms: List["Word"] = Relationship(
        back_populates="related_to",
        link_model=SynonymLink,
        sa_relationship_kwargs={
            "primaryjoin": "Word.id==SynonymLink.word_id",
            "secondaryjoin": "Word.id==SynonymLink.synonym_id",
        },
    )

    # Reverse synonyms
    related_to: List["Word"] = Relationship(
        back_populates="synonyms",
        link_model=SynonymLink,
        sa_relationship_kwargs={
            "primaryjoin": "Word.id==SynonymLink.synonym_id",
            "secondaryjoin": "Word.id==SynonymLink.word_id",
        },
    )

    @staticmethod
    def get_synonyms(session: SessionDep, word_text: str) -> Optional[List[str]]:
        """
            Retrieve all synonyms for a given word, including both direct and reverse relationships.

            This function performs a graph traversal starting from the provided word, collecting all
            words that are directly or indirectly linked through the SynonymLink table. This ensures
            that if any word is part of a synonym group (cluster), querying any of those words will
            return all the others in the group.

            Parameters:
            ----------
            session : Session
                The SQLModel database session used to perform queries.

            word_text : str
                The word whose synonyms are to be retrieved.

            Returns:
            -------
            Optional[List[str]]
                A list of unique synonym words (excluding the input word), or None if the word does not exist.

            Example:
            -------
            Assuming the following synonym relationships:
                - "happy" ↔ "cheerful"
                - "happy" ↔ "joyful"
                - "happy" ↔ "optimistic"

            Then:
                Word.get_synonyms(session, "happy") → ["cheerful", "joyful", "optimistic"]
                Word.get_synonyms(session, "cheerful") → ["happy", "joyful", "optimistic"]
                Word.get_synonyms(session, "unknownword") → None
            """
        start_word = session.exec(select(Word).where(Word.word == word_text)).first()
        if not start_word:
            return None

        visited_ids = set()
        synonym_words = set()
        queue = [start_word]

        while queue:
            current = queue.pop(0)
            if current.id in visited_ids:
                continue
            visited_ids.add(current.id)
            synonym_words.add(current.word)

            # Get both directions
            neighbors = current.synonyms + current.related_to
            for neighbor in neighbors:
                if neighbor.id not in visited_ids:
                    queue.append(neighbor)

        synonym_words.discard(word_text)  # remove self from result
        return list(synonym_words)
