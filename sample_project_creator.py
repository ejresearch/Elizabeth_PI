#!/usr/bin/env python3
"""
Lizzy Framework - Complete Sample Project Creator
Creates a full project with all data types for backend documentation/testing
"""

import os
import sqlite3
import json
import shutil
from datetime import datetime

def create_sample_source_material():
    """Create comprehensive source material for LightRAG buckets"""
    
    # Ensure bucket directories exist
    working_dir = "./lightrag_working_dir"
    buckets = ["books", "scripts", "plays"]
    
    for bucket in buckets:
        bucket_path = os.path.join(working_dir, bucket)
        os.makedirs(bucket_path, exist_ok=True)
    
    # Books bucket - Writing craft and theory
    books_content = {
        "story_structure_fundamentals.txt": """# STORY STRUCTURE FUNDAMENTALS

## The Three-Act Structure
Every compelling story follows a fundamental three-act structure that mirrors human psychological patterns.

### Act I - Setup (25% of story)
- **Ordinary World**: Establish character's normal life
- **Inciting Incident**: The event that changes everything  
- **Plot Point 1**: Character commits to the journey

### Act II - Confrontation (50% of story)
- **Rising Action**: Obstacles and complications increase
- **Midpoint**: Major revelation or plot twist
- **Plot Point 2**: All seems lost, darkest moment

### Act III - Resolution (25% of story)
- **Climax**: Final confrontation with main conflict
- **Falling Action**: Consequences of climax
- **Resolution**: New equilibrium established

## Character Arc Integration
The external plot must mirror the internal character transformation:
- External obstacles reflect internal fears
- Physical journey parallels emotional growth
- Resolution addresses both plot and character needs

## Conflict Layers
Effective stories operate on multiple conflict levels:
1. **Internal**: Character vs. self
2. **Interpersonal**: Character vs. character  
3. **Societal**: Character vs. society
4. **Universal**: Character vs. fate/nature

## Pacing and Rhythm
- **Scene vs. Sequel**: Action scenes followed by reflection
- **Rising Stakes**: Each obstacle more challenging than last
- **Emotional Beats**: Moments of connection between characters
- **Breathing Room**: Allow audience to process events

## Theme Expression
Theme emerges through:
- Character choices under pressure
- Consequences of actions
- Symbolic elements in setting
- Dialogue that reveals worldview
- Visual metaphors and motifs

Remember: Structure serves story, not the reverse.
""",

        "character_development_psychology.txt": """# CHARACTER DEVELOPMENT PSYCHOLOGY

## The Psychology of Compelling Characters
Great characters feel real because they're based on authentic psychological principles.

### Core Character Elements
1. **Conscious Goal**: What they think they want
2. **Unconscious Need**: What they actually need for growth
3. **Fatal Flaw**: The weakness that creates obstacles
4. **Backstory Wound**: Formative experience that shaped them

### Character Motivation Hierarchy
Following Maslow's hierarchy creates believable character drives:
- **Physiological**: Survival, safety, security
- **Social**: Love, belonging, acceptance  
- **Esteem**: Recognition, respect, achievement
- **Self-Actualization**: Purpose, meaning, transcendence

### Psychological Archetypes (Jung)
- **The Hero**: Seeks to prove worth through courage
- **The Mentor**: Guides others with wisdom
- **The Threshold Guardian**: Tests the hero's resolve
- **The Shapeshifter**: Represents uncertainty and betrayal
- **The Shadow**: Embodies the hero's dark side
- **The Ally**: Provides companionship and support
- **The Trickster**: Brings comic relief and perspective

### Character Contradictions
Realistic characters contain contradictions:
- The brave person who fears intimacy
- The kind person who can be ruthlessly competitive
- The intellectual who makes emotional decisions
- The cynic who secretly believes in love

### Dialogue and Voice
Each character needs distinct voice patterns:
- **Vocabulary**: Education, region, profession
- **Rhythm**: Fast/slow, choppy/flowing
- **Subtext**: What they don't say directly
- **Emotional Filter**: How worldview colors speech

### Character Relationships
Characters define themselves through relationships:
- **Opposition**: What they push against
- **Alliance**: Who they trust and support
- **Romance**: Vulnerability and intimacy
- **Mentorship**: Teaching and learning dynamics

### Growth and Change
Character transformation requires:
- **Resistance**: Why change is difficult
- **Catalyst**: Events that force change
- **Choice Points**: Moments requiring growth
- **Integration**: New self becomes natural

The most memorable characters surprise us while remaining true to their core nature.
""",

        "genre_conventions_modern_drama.txt": """# GENRE CONVENTIONS: MODERN DRAMA

## Defining Modern Drama
Modern drama emerged in the 20th century, focusing on psychological realism and social issues.

### Key Characteristics
- **Psychological Realism**: Characters behave according to believable psychology
- **Social Commentary**: Stories address contemporary issues
- **Moral Ambiguity**: Right and wrong aren't clearly defined
- **Understated Emotion**: Subtext more important than explicit statements
- **Naturalistic Dialogue**: Speech patterns mirror real conversation

### Structural Elements
- **Slow Burn**: Tension builds gradually through small moments
- **Character-Driven**: Plot emerges from character decisions
- **Multiple Perspectives**: Various viewpoints on central situation
- **Ambiguous Endings**: Resolution doesn't answer all questions
- **Thematic Complexity**: Multiple layers of meaning

### Visual Storytelling
- **Naturalistic Settings**: Locations feel lived-in and real
- **Intimate Cinematography**: Close-ups reveal internal states
- **Symbolic Objects**: Props carry emotional weight
- **Seasonal Metaphors**: Weather/time reflects emotional states
- **Architectural Psychology**: Spaces reflect character dynamics

### Dialogue Conventions
- **Subtext Heavy**: Characters rarely say what they mean
- **Interruptions**: Natural overlapping and cutting off
- **Silence**: What's not said is often most important
- **Class/Regional Markers**: Speech reflects background
- **Generational Differences**: Age affects communication style

### Common Themes
- **Identity Crisis**: Who am I really?
- **Family Dysfunction**: Toxic patterns and healing
- **Class Conflict**: Economic tensions and social mobility
- **Moral Compromise**: Ethical dilemmas with no clear answers
- **Urban Alienation**: Isolation in modern society
- **Gender Roles**: Changing expectations and relationships

### Emotional Tone
- **Melancholic**: Underlying sadness about human condition
- **Hopeful Despair**: Finding meaning despite difficulties
- **Quiet Intensity**: Powerful emotions expressed subtly
- **Bittersweet**: Joy and sorrow intermingled
- **Contemplative**: Space for audience reflection

### Pacing Rhythms
- **Contemplative Moments**: Characters process emotions
- **Escalating Tension**: Conflicts build through small incidents
- **Explosive Releases**: Brief moments of intense emotion
- **Return to Normalcy**: Characters attempt to restore balance

Modern drama requires patience from audiences but rewards with deep emotional truth.
"""
    }
    
    # Scripts bucket - Professional screenplays analysis
    scripts_content = {
        "ordinary_people_analysis.txt": """# ORDINARY PEOPLE (1980) - Screenplay Analysis

## Overview
Winner of Best Picture Oscar, directed by Robert Redford. A masterclass in family drama and psychological realism.

## Story Structure
**Setup**: Upper-middle-class family dealing with aftermath of older son's accidental death
**Inciting Incident**: Younger son Conrad attempts suicide
**Plot Point 1**: Conrad starts therapy with Dr. Berger
**Midpoint**: Conrad remembers the boating accident details
**Plot Point 2**: Conrad and mother Beth have explosive confrontation
**Climax**: Beth leaves the family
**Resolution**: Father and son achieve new understanding

## Character Analysis

### Conrad Jarrett (Son)
- **Conscious Goal**: Return to normal life after hospitalization
- **Unconscious Need**: Process grief and guilt over brother's death
- **Fatal Flaw**: Overwhelming guilt and self-blame
- **Arc**: From self-destruction to self-acceptance

### Calvin Jarrett (Father)  
- **Conscious Goal**: Keep family together
- **Unconscious Need**: Stop enabling Beth's emotional unavailability
- **Fatal Flaw**: Conflict avoidance and people-pleasing
- **Arc**: From passive enabler to protective parent

### Beth Jarrett (Mother)
- **Conscious Goal**: Maintain family's social standing
- **Unconscious Need**: Face her own grief and inadequacy
- **Fatal Flaw**: Emotional rigidity and perfectionism
- **Arc**: Static character who refuses growth

## Dialogue Techniques
- **Subtext**: Family members rarely state feelings directly
- **Class Markers**: Dialogue reflects upper-middle-class background
- **Therapy Scenes**: Professional language contrasts with family evasion
- **Generational Differences**: Parents and teen speak different emotional languages

## Visual Storytelling
- **Seasonal Progression**: Fall to winter mirrors emotional journey
- **Domestic Spaces**: House becomes increasingly cold and empty
- **Mirrors**: Reflections show characters' internal states
- **Water Imagery**: Lake represents both tragedy and cleansing

## Thematic Elements
- **Survival Guilt**: Why did I live when he died?
- **Perfectionism**: The cost of maintaining appearances
- **Communication**: How families fail to connect emotionally
- **Class and Therapy**: Privileged resistance to psychological help
- **Masculine Emotion**: Men learning to express feelings

## Technical Excellence
- **Scene Transitions**: Smooth cuts that advance both plot and character
- **Exposition**: Information revealed naturally through conflict
- **Pacing**: Slow burn that builds to emotional explosions
- **Ending**: Hopeful but realistic resolution

## Learning Points
- Family dysfunction creates compelling drama
- Internal conflict must drive external plot
- Authenticity in dialogue creates believable characters
- Subtext more powerful than explicit statements
- Resolution doesn't require fixing everyone
""",

        "manchester_by_the_sea_structure.txt": """# MANCHESTER BY THE SEA (2016) - Structural Analysis

## Overview
Written and directed by Kenneth Lonergan. Winner of Best Original Screenplay Oscar.

## Non-Linear Structure
The script uses a complex timeline that reveals information strategically:

### Present Timeline
- Lee returns to Manchester for brother's funeral
- Becomes guardian of nephew Patrick
- Attempts to fulfill responsibilities while emotionally numb

### Past Timeline (Revealed Through Flashbacks)
- Lee's marriage to Randi
- The fire that killed his children
- Breakdown of his marriage
- Self-imposed exile to Boston

## Character Study: Lee Chandler

### Psychological Profile
- **Trauma Response**: Emotional shutdown and self-punishment
- **Guilt Complex**: Believes he doesn't deserve happiness or redemption
- **Avoidance Pattern**: Removes himself from anything meaningful
- **Protective Mechanism**: Anger keeps people at distance

### Character Contradictions
- Responsible but runs from responsibility
- Caring but appears cold and detached
- Intelligent but makes self-destructive choices
- Strong but completely broken inside

## Dialogue Mastery

### Regional Authenticity
- Working-class Massachusetts dialect
- Blue-collar vocabulary and rhythm
- Generational speech patterns
- Cultural references specific to area

### Emotional Subtext
- Characters talk around feelings rather than about them
- Humor used to deflect serious emotions
- Silence carries as much weight as words
- Repetitive phrases show mental patterns

## Visual Storytelling Elements

### Setting as Character
- Manchester: Represents past trauma and family history
- Boston: Symbolizes escape and emotional numbness
- Ocean: Both beautiful and threatening presence
- Winter: Emotional coldness made literal

### Symbolic Objects
- Boat: Connection to brother and happier past
- Tools: Practical work vs. emotional work
- Basement: Literal and metaphorical foundation issues
- Food: Attempts at normal domestic life

## Thematic Depth

### Central Themes
- **Irrevocable Loss**: Some things can't be fixed or healed
- **Survivor's Guilt**: Living with unbearable responsibility
- **Masculine Grief**: How men process trauma differently
- **Community**: Small town support and judgment
- **Redemption Limits**: Not everyone gets a happy ending

### Social Commentary
- Working-class family dynamics
- Mental health stigma in blue-collar communities
- Economic pressure on family relationships
- Gender roles in crisis situations

## Technical Innovation

### Flashback Integration
- Memories triggered by present-day events
- Information revealed to serve character development
- Past and present inform each other continuously
- Audience discovers truth alongside protagonist

### Pacing Strategy
- Slow revelation builds emotional investment
- Mundane moments carry deep significance
- Explosive emotions followed by quiet processing
- Realistic timeline for grief and healing

## Writing Lessons
- Authenticity in regional voice creates believability
- Character trauma must drive all story decisions
- Some stories don't end with redemption or healing
- Subtext and silence often more powerful than exposition
- Structure can serve character psychology rather than plot convenience

This screenplay demonstrates how modern drama can achieve profound emotional impact through realistic character study and authentic dialogue.
"""
    }
    
    # Plays bucket - Theatrical works
    plays_content = {
        "death_of_salesman_character_study.txt": """# DEATH OF A SALESMAN - Character Study

## Willy Loman: The Tragic Everyman

Arthur Miller's masterpiece creates one of American theater's most complex protagonists.

### Character Psychology
- **Self-Deception**: Lives in fantasy rather than face reality
- **Identity Crisis**: Worth tied entirely to professional success
- **Father Wound**: Abandoned by own father, struggles to be good parent
- **American Dream Victim**: Believes success equals worth as human being

### Dialogue Patterns
- **Repetitive Phrases**: "I'm well liked" becomes desperate mantra
- **Time Confusion**: Past and present blend in his deteriorating mind
- **Sales Language**: Treats family relationships like business transactions
- **Denial Statements**: Constantly contradicts obvious truths

### Relationship Dynamics

#### With Linda (Wife)
- She enables his self-deception out of love
- Protects him from reality while enabling destruction
- Represents loyalty and long-suffering devotion
- Her practicality contrasts with his fantasies

#### With Biff (Son)
- Projection of his own failed dreams
- Relationship damaged by discovery of affair
- Represents wasted potential and disillusionment
- Love complicated by disappointment and guilt

#### With Happy (Son)
- Ignored son who still seeks approval
- Inherits father's value system without questioning
- Represents perpetuation of destructive patterns
- More successful but equally empty

## Thematic Elements

### The American Dream Critique
- Success measured only by material wealth
- Individual worth tied to professional achievement
- Competition destroys authentic relationships
- System promises more than it can deliver

### Masculinity and Identity
- Male worth defined by providing for family
- Professional failure equals personal failure
- Emotional expression seen as weakness
- Legacy concerns and generational pressure

### Time and Memory
- Past intrudes on present constantly
- Memory unreliable and self-serving
- Nostalgia for imagined golden age
- Future holds only fear and uncertainty

## Structural Analysis

### Expressionistic Elements
- Memory scenes blend with reality
- Set design reflects psychological state
- Music and lighting support internal world
- Characters appear and disappear fluidly

### Tragic Structure
- **Hamartia**: Pride and self-deception
- **Peripeteia**: Son's rejection of his values
- **Anagnorisis**: Moment of self-recognition (limited)
- **Catharsis**: Death as final failed sales pitch

## Language and Dialogue

### Working-Class Authenticity
- Brooklyn dialect and speech patterns
- Limited vocabulary but emotional directness
- Clichés reflect cultural programming
- Interrupted and overlapping conversations

### Symbolic Language
- Sales terminology applied to life
- Garden imagery represents growth and fertility
- Car represents both freedom and death
- House symbolizes both shelter and trap

## Contemporary Relevance
- Economic anxiety and job insecurity
- Identity tied to career success
- Generational conflict over values
- Mental health stigma in families
- Masculine identity crisis in changing economy

## Performance Considerations
- Actor must balance sympathy with frustration
- Energy levels vary from manic to depressive
- Physical deterioration mirrors mental decline
- Requires authentic working-class demeanor
- Must make self-deception believable

This character study reveals how Miller created a universal figure whose struggles remain relevant across generations.
""",

        "realistic_dialogue_techniques.txt": """# REALISTIC DIALOGUE TECHNIQUES IN THEATER

## Foundations of Naturalistic Speech

### Observational Research
- **Eavesdropping**: Listen to real conversations in public spaces
- **Regional Variations**: Study dialect, rhythm, and vocabulary patterns
- **Class Markers**: Notice how education and economics affect speech
- **Generational Differences**: Age groups have distinct communication styles
- **Professional Language**: Occupations create specific vocabularies

### Speech Pattern Elements
- **Interruptions**: People rarely wait for others to finish
- **Overlapping**: Multiple speakers talking simultaneously
- **Incomplete Thoughts**: Sentences trail off or change direction
- **Repetition**: Important points get restated multiple ways
- **Filler Words**: "Um," "uh," "you know," "like" feel natural

## Character Voice Development

### Individual Speech Signatures
Each character needs distinctive verbal patterns:
- **Vocabulary Level**: Formal vs. colloquial word choices
- **Sentence Length**: Short bursts vs. complex constructions
- **Rhythm**: Fast-paced vs. deliberate delivery
- **Emotional Range**: Expressive vs. controlled communication
- **Cultural Background**: Regional, ethnic, religious influences

### Psychological Markers
- **Anxiety**: Rushed speech, repeated phrases, verbal tics
- **Depression**: Minimal responses, trailing sentences, long pauses
- **Anger**: Clipped words, curse patterns, volume changes
- **Intelligence**: Complex syntax vs. simple declarative statements
- **Deception**: Verbal evasion, over-explanation, defensive language

## Subtext and Implication

### What Characters Don't Say
- **Emotional Avoidance**: Talking around feelings instead of about them
- **Social Propriety**: What's inappropriate to state directly
- **Power Dynamics**: Hierarchy affects who can say what
- **Shame and Secrets**: Topics too painful to address openly
- **Cultural Taboos**: Subjects that can't be mentioned directly

### Revealing Subtext Through:
- **Word Choice**: Selecting terms that carry hidden meaning
- **Timing**: When characters choose to speak or stay silent
- **Repetition**: Obsessive return to certain topics
- **Deflection**: Changing subjects to avoid confrontation
- **Body Language**: Physical contradictions to verbal statements

## Technical Dialogue Craft

### Exposition Integration
- **Natural Information Flow**: Characters share what they logically would
- **Conflict-Driven Revelation**: Information emerges through disagreement
- **Emotional Stakes**: Facts matter because characters care about them
- **Gradual Disclosure**: Audience learns alongside characters
- **Multiple Perspectives**: Different characters provide different details

### Rhythm and Pacing
- **Stichomythia**: Rapid-fire short exchanges build tension
- **Monologue Moments**: Extended speeches reveal character depth
- **Pause Power**: Silence creates emphasis and emotional weight
- **Overlapping Speech**: Naturalistic conversation flow
- **Tempo Changes**: Varying pace maintains audience interest

## Genre-Specific Considerations

### Family Drama
- **Shared History**: References to past events and inside jokes
- **Generational Language**: Different age groups speak differently
- **Emotional Shorthand**: Family members communicate in abbreviated ways
- **Conflict Patterns**: Repetitive arguments reveal relationship dynamics
- **Love and Frustration**: Affection expressed through irritation

### Social Realism
- **Class Consciousness**: Economic status affects language choices
- **Political Awareness**: Characters reference social issues naturally
- **Work Language**: Professional vocabularies invade personal conversations
- **Cultural Specificity**: References to shared cultural experiences
- **Historical Context**: Time period influences available expressions

## Common Pitfalls to Avoid

### Artificial Elements
- **Information Dumps**: Characters explaining things they all know
- **Perfect Grammar**: Real speech includes errors and fragments
- **Constant Wit**: Not everyone is clever all the time
- **Thesis Statements**: Avoid characters speechifying about themes
- **Uniform Voice**: All characters sounding like the writer

### Realism Balance
- **Too Natural**: Actual speech patterns can be boring on stage
- **Performance Needs**: Actors need clear objectives and obstacles
- **Audience Comprehension**: Dialogue must serve story clarity
- **Theatrical Convention**: Some artifice serves dramatic purpose
- **Emotional Truth**: Feelings matter more than absolute realism

## Practice Exercises

### Voice Development
- Write the same information delivered by three different characters
- Create distinct speech patterns for various social classes
- Practice interruption and overlapping dialogue techniques
- Develop character-specific curse words and expressions
- Write subtext-heavy scenes where characters avoid direct communication

### Authenticity Research
- Transcribe real conversations and adapt for stage
- Study film/TV dialogue in your target genre
- Read plays known for excellent naturalistic dialogue
- Interview people from backgrounds different from your own
- Practice regional dialects and speech patterns

Mastering realistic dialogue requires balancing authenticity with theatrical effectiveness.
"""
    }
    
    # Write all content files
    for filename, content in books_content.items():
        with open(os.path.join(working_dir, "books", filename), 'w') as f:
            f.write(content)
    
    for filename, content in scripts_content.items():
        with open(os.path.join(working_dir, "scripts", filename), 'w') as f:
            f.write(content)
    
    for filename, content in plays_content.items():
        with open(os.path.join(working_dir, "plays", filename), 'w') as f:
            f.write(content)
    
    print("✅ Created comprehensive source material in buckets")
    return True

def create_sample_project():
    """Create a complete sample project: 'The Last Coffee Shop'"""
    
    project_name = "the_last_coffee_shop"
    projects_dir = "projects"
    project_dir = os.path.join(projects_dir, project_name)
    
    # Create project directory
    os.makedirs(project_dir, exist_ok=True)
    
    # Create project database
    db_path = os.path.join(project_dir, f"{project_name}.sqlite")
    
    # Remove existing database if it exists
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create all required tables
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS project_metadata (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        key TEXT UNIQUE NOT NULL,
        value TEXT NOT NULL,
        created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS characters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER,
        occupation TEXT,
        personality_traits TEXT,
        backstory TEXT,
        goals_motivation TEXT,
        conflicts_challenges TEXT,
        created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS story_outline (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        act_number INTEGER NOT NULL,
        scene_number INTEGER NOT NULL,
        scene_title TEXT NOT NULL,
        location TEXT NOT NULL,
        time_of_day TEXT,
        characters_present TEXT,
        scene_summary TEXT,
        key_events TEXT,
        emotional_beats TEXT,
        created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS brainstorming_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        scene_id INTEGER,
        tone_preset TEXT NOT NULL,
        user_input TEXT,
        rag_context TEXT,
        ai_response TEXT,
        session_notes TEXT,
        created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (scene_id) REFERENCES story_outline (id)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS finalized_draft_v1 (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        scene_id INTEGER,
        scene_content TEXT NOT NULL,
        formatting_notes TEXT,
        revision_notes TEXT,
        export_filename TEXT,
        created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (scene_id) REFERENCES story_outline (id)
    )
    ''')
    
    # Insert project metadata
    metadata_entries = [
        ('created_date', datetime.now().isoformat()),
        ('project_name', project_name),
        ('genre', 'Modern Drama'),
        ('logline', 'When the last independent coffee shop in a gentrifying neighborhood faces closure, three generations of regulars must confront what home really means.'),
        ('theme', 'Community, belonging, and resistance to change in modern urban life'),
        ('target_length', '15-20 minutes'),
        ('format', 'Short Film Screenplay'),
        ('status', 'In Development')
    ]
    
    for key, value in metadata_entries:
        cursor.execute('INSERT INTO project_metadata (key, value) VALUES (?, ?)', (key, value))
    
    # Insert detailed characters
    characters_data = [
        (
            'Maya Chen', 28, 'Coffee Shop Owner',
            'Passionate, stubborn, idealistic, protective of community spaces, struggles with business pragmatism vs. artistic vision',
            'Third-generation owner of The Grind coffee shop. Inherited the business from her grandmother who started it in the 1960s as a gathering place for artists and activists. Has an MFA in Creative Writing but chose to keep the family business alive. Recently divorced after her ex-husband criticized her for prioritizing the shop over their relationship.',
            'Save the coffee shop from closure while maintaining its authentic community character. Wants to honor her grandmother\'s legacy while making the business financially sustainable.',
            'Massive rent increase from new property management company. Declining customer base as neighborhood gentrifies. Personal isolation due to long work hours. Fear of failure and disappointing family legacy.'
        ),
        (
            'Frank Rodriguez', 67, 'Retired Teacher',
            'Wise, patient, observant, gentle humor, carries quiet sadness about life changes, natural mentor figure',
            'Retired high school English teacher who has been coming to The Grind for 15 years. Widowed three years ago after 40-year marriage to Elena. Has two adult children who live across the country. Spends most days at the coffee shop reading, grading papers for substitute teaching, and watching the neighborhood change around him.',
            'Find purpose and connection in retirement. Process grief over wife\'s death. Maintain sense of community as familiar places disappear.',
            'Loneliness since wife\'s death. Feeling displaced as neighborhood changes. Health concerns he doesn\'t discuss. Fear of being forgotten or becoming irrelevant.'
        ),
        (
            'Jordan Kim', 22, 'College Student/Barista',
            'Energetic, socially conscious, tech-savvy, idealistic about changing the world, impatient with older generations',
            'Senior at local university studying Urban Planning with minor in Social Justice. Works part-time at The Grind to pay for school. First-generation college student whose parents own a small grocery store in Koreatown. Active in campus organizing and local housing rights advocacy.',
            'Graduate and work on urban development that serves communities rather than displaces them. Help save The Grind as practice for larger community organizing work.',
            'Student loan debt and financial pressure. Tension between academic idealism and real-world complexity. Pressure from parents to focus on studies instead of activism. Impatience with slow pace of systemic change.'
        )
    ]
    
    for char_data in characters_data:
        cursor.execute('''
        INSERT INTO characters (name, age, occupation, personality_traits, backstory, goals_motivation, conflicts_challenges)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', char_data)
    
    # Insert story outline (3 scenes)
    scenes_data = [
        (
            1, 1, 'Morning Ritual',
            'The Grind Coffee Shop - Interior',
            'Early Morning (7:00 AM)',
            'Maya, Frank, Jordan',
            'Maya opens the shop for another day while Frank arrives for his regular morning routine. Jordan arrives for work shift. The comfortable rhythm of their daily interactions establishes the coffee shop as a community hub.',
            'Maya unlocks shop, starts machines; Frank enters with newspaper, exchanges familiar banter; Jordan arrives with energy and campus stories; Regular customers filter in; Maya discovers rent increase notice in mail',
            'Comfort of routine, community warmth, growing anxiety about business, intergenerational connections'
        ),
        (
            2, 1, 'The Notice',
            'The Grind Coffee Shop - Interior',
            'Mid-Morning (10:00 AM)',
            'Maya, Frank, Jordan',
            'Maya shares the devastating news about the rent increase with Frank and Jordan. The three characters react differently based on their generational perspectives and life experiences.',
            'Maya reveals 300% rent increase; Frank offers wisdom about previous neighborhood changes; Jordan proposes activist solutions; Discussion about gentrification and community values; Maya feels torn between fight and surrender',
            'Shock, anger, determination, fear, solidarity across generations'
        ),
        (
            3, 1, 'Last Call Decision',
            'The Grind Coffee Shop - Interior',
            'Late Afternoon (4:00 PM)',
            'Maya, Frank, Jordan, plus community members (background)',
            'As the day winds down, the three main characters reach a decision about how to respond to the crisis. The coffee shop fills with regular customers, emphasizing what would be lost.',
            'Community members arrive after hearing news; Impromptu planning session begins; Maya realizes shop means more than business; Decision to fight closure through community organizing; Frank offers life savings; Jordan mobilizes social media campaign',
            'Resolve, hope, community solidarity, bittersweet determination'
        )
    ]
    
    for scene_data in scenes_data:
        cursor.execute('''
        INSERT INTO story_outline (act_number, scene_number, scene_title, location, time_of_day, characters_present, scene_summary, key_events, emotional_beats)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', scene_data)
    
    conn.commit()
    conn.close()
    
    print(f"✅ Created complete project: {project_name}")
    return project_name

if __name__ == "__main__":
    print("🎬 Creating Complete Sample Project for Backend Documentation")
    print("=" * 60)
    
    # Step 1: Create source material
    create_sample_source_material()
    
    # Step 2: Create project
    project_name = create_sample_project()
    
    print(f"\n✅ Sample project '{project_name}' created successfully!")
    print("\n📋 Next steps:")
    print("1. Run: python lizzy.py")
    print("2. Select the project: the_last_coffee_shop")
    print("3. Go to Buckets Manager and ingest source material")
    print("4. Use brainstorming to generate scene content")
    print("5. Write all three scenes")
    print("6. Export complete documentation")