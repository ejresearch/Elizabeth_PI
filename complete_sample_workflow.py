#!/usr/bin/env python3
"""
Complete Sample Workflow Generator
Creates brainstorming sessions and scene content for documentation
"""

import sqlite3
import os
from datetime import datetime

def add_brainstorming_sessions():
    """Add comprehensive brainstorming sessions for all scenes"""
    
    project_name = "the_last_coffee_shop"
    db_path = f"projects/{project_name}/{project_name}.sqlite"
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Brainstorming sessions for each scene
    brainstorm_data = [
        {
            'scene_id': 1,
            'tone_preset': 'Modern Indie',
            'user_input': 'Opening scene showing morning routine and community connections at coffee shop',
            'rag_context': '''
            Retrieved from books bucket: "Structure serves story - establish ordinary world and character relationships before inciting incident. Morning rituals create intimacy and show what's at stake."
            
            Retrieved from scripts bucket: "Visual storytelling through domestic spaces - locations should feel lived-in and real. Intimate cinematography reveals internal states."
            
            Retrieved from plays bucket: "Realistic dialogue uses subtext, interruptions, and character-specific speech patterns. Family dynamics reveal generational conflicts."
            ''',
            'ai_response': '''
            OPENING SCENE CONCEPT - "Morning Ritual"
            
            VISUAL APPROACH:
            - Start with extreme close-ups of coffee preparation ritual
            - Maya's hands moving through familiar motions with muscle memory
            - Steam, grinding sounds, mechanical precision masking emotional uncertainty
            - Gradually widen to reveal the full space and its character
            
            CHARACTER DYNAMICS:
            - Maya: Professional competence hiding personal struggles
            - Frank: Observant, notices small changes in others' behavior  
            - Jordan: Energy and optimism contrasting with adults' wariness
            
            DIALOGUE PATTERNS:
            - Maya: Clipped, efficient, task-focused speech when stressed
            - Frank: Gentle probing, uses questions to show care
            - Jordan: Overlapping speech, interrupts with enthusiasm
            
            SUBTLE FORESHADOWING:
            - Maya avoiding opening mail pile
            - Frank commenting on "changes in the neighborhood"
            - Jordan's idealistic comments about "community spaces"
            
            EMOTIONAL UNDERTONE:
            - Comfort of routine masking underlying anxiety
            - Intergenerational care expressed through small gestures
            - Brewing tension about unspoken concerns
            
            This scene should feel like a warm embrace before the conflict arrives.
            ''',
            'session_notes': 'Focus on establishing character relationships and daily rhythms. The coffee shop as sanctuary needs to be felt before it\'s threatened.'
        },
        {
            'scene_id': 2,
            'tone_preset': 'Romantic Dramedy',
            'user_input': 'Scene where Maya reveals the rent increase crisis - how do three generations respond differently?',
            'rag_context': '''
            Retrieved from books bucket: "Character contradictions create realism - the brave person who fears intimacy, the kind person who can be ruthlessly competitive. Each character filters information through their worldview."
            
            Retrieved from scripts bucket: "Conflict layers: Internal (character vs self), Interpersonal (character vs character), Societal (character vs society). Multiple perspectives on central situation create depth."
            
            Retrieved from plays bucket: "Working-class authenticity - economic anxiety affects dialogue patterns. Generational differences in communication style and problem-solving approaches."
            ''',
            'ai_response': '''
            CRISIS REVELATION SCENE - "The Notice"
            
            GENERATIONAL RESPONSE PATTERNS:
            
            MAYA (28) - Millennial Overwhelm:
            - Immediately starts problem-solving with spreadsheets and calculations
            - References similar closures in other neighborhoods
            - Feels personal responsibility and failure
            - "I should have seen this coming, should have saved more..."
            
            FRANK (67) - Historical Perspective:
            - Draws parallels to previous neighborhood changes he's witnessed
            - Offers wisdom about community resilience and adaptation
            - Practical suggestions based on life experience
            - "This isn't the first time, won't be the last. Question is what we do about it."
            
            JORDAN (22) - Gen Z Activism:
            - Immediately thinks in terms of systemic solutions
            - References tenant rights, community organizing, social media campaigns
            - Optimistic about collective action possibilities
            - "We need to document everything, build coalition, make this about more than just one shop."
            
            EMOTIONAL BEATS:
            - Initial shock → Processing → Different coping mechanisms emerge
            - Maya: Inward collapse then desperate planning
            - Frank: Steady presence, becomes emotional anchor
            - Jordan: Anger that transforms into organizing energy
            
            DIALOGUE TEXTURE:
            - Numbers and financial reality punctuating emotional responses
            - Characters talking over each other as urgency builds
            - Frank's measured responses grounding the younger characters' reactivity
            - Economic terms mixing with emotional language
            
            VISUAL METAPHOR:
            - The notice itself as physical object passed between characters
            - Coffee getting cold and forgotten as crisis unfolds
            - Afternoon light shifting, time passing unnoticed
            ''',
            'session_notes': 'Each character\'s response reveals their worldview and coping mechanisms. The scene should feel like watching three different generations face the same crisis.'
        },
        {
            'scene_id': 3,
            'tone_preset': 'Cheesy Romcom',
            'user_input': 'Final scene where community comes together to fight closure - balance hope with realism',
            'rag_context': '''
            Retrieved from books bucket: "Resolution addresses both plot and character needs. Theme emerges through character choices under pressure. New equilibrium established that honors what came before."
            
            Retrieved from scripts bucket: "Ambiguous endings - resolution doesn't answer all questions. Hopeful despair - finding meaning despite difficulties. Bittersweet tone with joy and sorrow intermingled."
            
            Retrieved from plays bucket: "Community support and judgment in small spaces. Economic pressure on family relationships. Working-class solidarity patterns and mutual aid traditions."
            ''',
            'ai_response': '''
            COMMUNITY RALLY SCENE - "Last Call Decision"
            
            ESCALATING SOLIDARITY:
            - Word spreads through neighborhood networks (not just social media)
            - Regular customers arrive with "what can we do?" energy
            - Different types of support offered based on individual capabilities
            - Scene builds from intimate trio to small community gathering
            
            REALISTIC HOPE:
            - No magic solutions or sudden windfalls
            - Frank's offer of life savings is significant but not enough alone
            - Jordan's organizing skills provide structure but not guarantees
            - Maya's realization that fighting means accepting help from others
            
            CHARACTER GROWTH MOMENTS:
            - Maya: From isolated business owner to community organizer
            - Frank: From passive observer to active participant in change
            - Jordan: From abstract idealism to practical community work
            
            LAYERED DIALOGUE:
            - Business planning mixed with emotional support
            - Multiple conversations happening simultaneously
            - Code-switching as different community members arrive
            - Practical details grounding emotional declarations
            
            VISUAL STORYTELLING:
            - Coffee shop filling with people creates literal warmth
            - Diverse ages and backgrounds represented in crowd
            - Makeshift planning with napkin notes and phone numbers
            - Late afternoon light suggesting both endings and beginnings
            
            BITTERSWEET RESOLUTION:
            - Clear that the fight will be difficult and outcome uncertain
            - Community bond strengthened regardless of ultimate success
            - Characters have grown and relationships deepened
            - Ending suggests process more important than guaranteed outcome
            
            THEMATIC PAYOFF:
            - Home isn't just a place but the people who care about it
            - Individual struggle becomes collective action
            - Economic crisis reveals true community values
            - Hope exists in mutual support, not easy answers
            ''',
            'session_notes': 'Avoid false sentimentality while maintaining genuine emotional hope. The resolution should feel earned through character growth, not plot convenience.'
        }
    ]
    
    for session in brainstorm_data:
        cursor.execute('''
        INSERT INTO brainstorming_log (scene_id, tone_preset, user_input, rag_context, ai_response, session_notes)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (session['scene_id'], session['tone_preset'], session['user_input'], 
              session['rag_context'], session['ai_response'], session['session_notes']))
    
    conn.commit()
    conn.close()
    print(" Added comprehensive brainstorming sessions")

def add_scene_content():
    """Add complete screenplay scenes"""
    
    project_name = "the_last_coffee_shop"
    db_path = f"projects/{project_name}/{project_name}.sqlite"
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    scenes_content = [
        {
            'scene_id': 1,
            'scene_content': '''FADE IN:

EXT. URBAN STREET - EARLY MORNING (7:00 AM)

A gentrifying neighborhood in transition. New luxury condos tower over older brick buildings. Construction noise echoes in the distance.

THE GRIND COFFEE SHOP sits nestled between a trendy boutique and a "For Lease" sign.

INT. THE GRIND COFFEE SHOP - CONTINUOUS

MAYA CHEN (28), focused and efficient, moves through her opening routine with practiced precision. Coffee machines hum to life. The space feels lived-in: mismatched furniture, local art on walls, community bulletin board overflowing with notices.

Maya avoids looking at a pile of unopened mail on the counter.

SOUND of keys at the door. FRANK RODRIGUEZ (67) enters with his newspaper and gentle smile.

                    FRANK
          Morning, Maya. The usual suspects are
          gathering for the breakfast rush, I see.

                    MAYA
               (forcing brightness)
          Frank! Right on time. Colombian dark roast
          is ready to go.

Frank settles at his regular table by the window, spreading out his newspaper. Maya brings his coffee without being asked.

                    FRANK
          You know, I've been watching this
          neighborhood change for fifteen years.
          But some things stay constant.

                    MAYA
          Like your 7 AM arrival?

                    FRANK
          Like good coffee and better company.

The door chimes as JORDAN KIM (22) bursts in with student energy, backpack slung over shoulder.

                    JORDAN
          Sorry I'm late! Professor Martinez kept
          us after to talk about the housing
          forum next week. Maya, you should come.
          It's all about preserving community
          spaces and—

                    MAYA
          Jordan, apron first, activism second.
          We've got the morning rush starting.

Jordan ties on their apron, still talking.

                    JORDAN
          I'm just saying, there's this whole
          movement about protecting local
          businesses from predatory landlords—

                    FRANK
               (gently)
          What kind of forum?

                    JORDAN
          Community organizing. Getting people
          together to fight back against
          displacement. It's happening everywhere
          but nobody talks about it until it's
          too late.

Maya's hands pause while wiping down the espresso machine. She glances at the mail pile.

SOUND of the door chime as regular customers begin filtering in. The coffee shop comes alive with morning conversation, clinking cups, steaming milk.

Maya, Frank, and Jordan fall into their familiar rhythm – but underneath, tension brews like strong coffee.

Maya finally approaches the mail pile, her hand hovering over an official-looking envelope.

                    MAYA
               (quietly)
          Sometimes talking about it doesn't make
          it less scary.

She picks up the envelope. Her expression changes as she reads the return address.

FREEZE FRAME on Maya's face as realization hits.

FADE TO BLACK.

END OF SCENE 1''',
            'formatting_notes': 'Standard screenplay format with proper scene headings, character introductions, and action lines. Dialogue reflects character voices established in development.',
            'revision_notes': 'Enhanced visual details and subtext. Added foreshadowing through Jordan\'s activism discussion and Maya\'s avoidance of mail. Strengthened character-specific dialogue patterns.',
            'export_filename': 'last_coffee_shop_scene1_v1.txt'
        },
        {
            'scene_id': 2,
            'scene_content': '''INT. THE GRIND COFFEE SHOP - MID-MORNING (10:00 AM)

The breakfast rush has settled. A few customers work on laptops. Frank still sits at his table, newspaper now folded. Jordan restocks pastries behind the counter.

Maya stands frozen, holding the opened envelope. Her face is pale.

                    FRANK
          Maya? Everything alright?

Maya looks up, the letter trembling slightly in her hands.

                    MAYA
          They're... they're raising the rent.

                    JORDAN
          Who's raising what now?

                    MAYA
               (reading from letter)
          "New property management company...
          market rate adjustment... three hundred
          percent increase effective next month."

Jordan drops the pastry they're holding.

                    JORDAN
          Three hundred percent? That's...
          that's impossible.

                    FRANK
               (standing, moving toward Maya)
          Let me see that.

Frank takes the letter, his teacher instincts kicking in. He reads silently, his expression growing grave.

                    FRANK
          This is real. Phoenix Property Group.
          I've seen their signs going up all
          over the neighborhood.

                    MAYA
               (collapsing onto a stool)
          I can't pay this. Nobody could pay
          this. It's designed to...

                    JORDAN
          To force you out. This is exactly what
          I was talking about. Predatory capitalism
          disguised as market improvement.

                    FRANK
               (to Jordan)
          Take it down a notch. Maya needs support,
          not a lecture.

                    JORDAN
          I'm not lecturing! I'm saying we can
          fight this. There are tenant rights,
          community organizing strategies—

                    MAYA
          Jordan, this isn't your urban planning
          textbook. This is my grandmother's
          coffee shop. This is my life.

                    FRANK
               (settling next to Maya)
          What was the old rent?

                    MAYA
          Twenty-eight hundred a month. Now they
          want eighty-four hundred. Plus utilities.
          Plus "facility improvement fees."

                    JORDAN
               (pulling out phone)
          Okay, I'm looking up Phoenix Property
          Group right now. There have to be other
          businesses dealing with the same thing.
          If we organize together—

                    MAYA
          Stop. Just... stop for a minute.

Silence falls. A customer orders a latte; Jordan serves them mechanically.

                    FRANK
          You know, in 1987, they tried to tear
          down the community center where I taught
          night classes. We fought it.

                    MAYA
          Did you win?

                    FRANK
          We delayed it five years. Got better
          terms. Sometimes that's all you can do.

                    JORDAN
               (returning to conversation)
          But sometimes you can win completely.
          My cousin in Oakland saved their family
          restaurant through community pressure.
          Social media campaigns, city council
          meetings, boycotts of the management
          company...

                    MAYA
          This isn't Oakland, Jordan. And I'm
          not your cousin.

                    FRANK
          What would your grandmother do?

Maya looks around the coffee shop, taking in the community photos on the walls, the worn but cared-for furniture.

                    MAYA
          She'd probably serve them coffee and
          make them feel guilty about destroying
          something beautiful.

                    JORDAN
          Or she'd organize the whole neighborhood
          to fight back.

                    MAYA
          She'd... she'd ask what the community
          needed.

The three sit in contemplative silence as the weight of the decision settles around them.

FADE TO BLACK.

END OF SCENE 2''',
            'formatting_notes': 'Maintains emotional pacing while advancing plot. Each character responds according to established personality and generational perspective.',
            'revision_notes': 'Added more specific financial details to ground the crisis in reality. Enhanced Frank\'s role as emotional anchor. Strengthened Maya\'s connection to family legacy.',
            'export_filename': 'last_coffee_shop_scene2_v1.txt'
        },
        {
            'scene_id': 3,
            'scene_content': '''INT. THE GRIND COFFEE SHOP - LATE AFTERNOON (4:00 PM)

The afternoon light streams through windows, casting long shadows. Word has spread through the neighborhood. The coffee shop buzzes with an unusual energy.

REGULAR CUSTOMERS sit at various tables: MARIA (40s, teacher), DAVID (30s, mechanic), ELENA (50s, accountant), CARLOS (60s, retired postal worker). Everyone looks concerned but determined.

Maya, Frank, and Jordan stand behind the counter, looking overwhelmed by the response.

                    MARIA
          We heard about the rent situation.
          What can we do?

                    DAVID
          My shop got hit with the same thing
          last year. Different property company,
          same playbook.

                    ELENA
          I can look at your books, see if
          there are any financial options.

Maya wipes her eyes, emotional at the outpouring of support.

                    MAYA
          I don't know what to say. I thought...
          I thought I'd have to handle this alone.

                    FRANK
               (stepping forward)
          You're not alone. This place matters
          to all of us.

                    JORDAN
               (energized)
          Okay, so what are our options? Legal
          challenges, media pressure, community
          organizing, fundraising...

                    CARLOS
          In my day, we'd have a sit-in.

                    ELENA
          In my day, we'd check if they filed
          the proper permits and improvements
          to justify the increase.

                    DAVID
          In my day, we'd figure out who their
          other clients are and make some noise.

                    MAYA
               (laughing despite herself)
          Apparently every day is our day.

Frank pulls out his checkbook, writing carefully.

                    FRANK
          Elena and I started saving for a trip
          we'll never take. I want you to have this.

He hands Maya a check. She looks at it and gasps.

                    MAYA
          Frank, I can't accept this. This is
          your life savings.

                    FRANK
          Maya, this IS my life. This place,
          these people. Elena would understand.

                    JORDAN
               (showing phone)
          I started a crowdfunding campaign.
          We've already got three hundred dollars
          and I only posted it an hour ago.

                    MARIA
          The teachers' union has a discretionary
          fund for community support. I can
          make some calls.

                    DAVID
          My customers are mostly contractors.
          We know about dealing with property
          management companies. I can ask around.

Maya looks around the room at all these faces – her community, her chosen family.

                    MAYA
          This might not work. We might fight
          and still lose the shop.

                    ELENA
          But we won't lose each other.

                    JORDAN
          And we won't go down without a fight.

                    FRANK
          Sometimes the fight itself is the victory.

Maya takes a deep breath, straightening her shoulders.

                    MAYA
          Okay. Let's figure out how to save
          The Grind.

The group huddles together, pulling out phones, notebooks, business cards. Energy builds as plans take shape.

SOUND of the espresso machine hissing, blending with animated conversation. Through the window, the neighborhood continues its daily rhythm, unaware that something important is beginning inside this small coffee shop.

                    MAYA (V.O.)
          My grandmother always said the most
          important ingredient in coffee is
          the people you share it with.

CAMERA PULLS BACK slowly through the window as the community planning session continues, their heads bent together over napkin sketches and shared determination.

FADE TO BLACK.

THE END

TITLE CARD: "The Last Coffee Shop" was inspired by community struggles happening in neighborhoods across America. For resources on tenant organizing and small business advocacy, visit [community resource website].

FINAL FADE OUT.''',
            'formatting_notes': 'Resolution balances hope with realism. Community support feels authentic rather than magical. Ending suggests ongoing struggle rather than easy victory.',
            'revision_notes': 'Added more diverse community voices to show neighborhood demographics. Enhanced emotional authenticity of Maya\'s journey from isolation to connection. Strengthened thematic payoff.',
            'export_filename': 'last_coffee_shop_scene3_v1.txt'
        }
    ]
    
    for scene in scenes_content:
        cursor.execute('''
        INSERT INTO finalized_draft_v1 (scene_id, scene_content, formatting_notes, revision_notes, export_filename)
        VALUES (?, ?, ?, ?, ?)
        ''', (scene['scene_id'], scene['scene_content'], scene['formatting_notes'], 
              scene['revision_notes'], scene['export_filename']))
    
    conn.commit()
    conn.close()
    print(" Added complete screenplay scenes")

if __name__ == "__main__":
    print(" Completing Sample Project with Full Content")
    print("=" * 50)
    
    add_brainstorming_sessions()
    add_scene_content()
    
    print("\n Sample project now contains:")
    print("   • Complete character development")
    print("   • Detailed story outline") 
    print("   • Comprehensive brainstorming sessions")
    print("   • Full screenplay scenes with formatting")
    print("   • Rich source material in LightRAG buckets")
    print("\n🚀 Ready for complete data export!")